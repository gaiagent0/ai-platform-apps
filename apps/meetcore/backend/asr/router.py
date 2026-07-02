"""ASR REST + WebSocket endpoints."""
import json, logging, struct, io, wave
from fastapi import APIRouter, File, Form, UploadFile, WebSocket, WebSocketDisconnect, HTTPException
from . import service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/asr", tags=["ASR"])

@router.get("/health")
async def asr_health():
    return await service.health_all()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: str = Form(default="hu"), backend: str = Form(default="auto")):
    audio_bytes = await file.read()
    try:
        text, used_backend = await service.transcribe_audio(audio_bytes, language, backend)
        return {"text": text, "language": language, "backend": used_backend}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@router.websocket("/ws/live")
async def live_asr(ws: WebSocket):
    await ws.accept()
    logger.info("[LiveASR] WebSocket connected")
    pcm_buffer = bytearray()
    silence_frames = 0
    segment_count = 0
    language = "hu"
    SILENCE_THRESHOLD = 300.0
    SILENCE_MS = 1500
    FRAME_MS = 30
    FRAME_SIZE = 16000 * 2 * FRAME_MS // 1000
    SILENCE_FRAMES_LIMIT = SILENCE_MS // FRAME_MS
    CHUNK_MIN_BYTES = 500 * 16000 * 2 // 1000

    def rms_energy(data):
        if len(data) < 2:
            return 0.0
        aligned = data[:len(data)-len(data)%2]
        samples = struct.unpack(f"<{len(aligned)//2}h", aligned)
        return (sum(s*s for s in samples)/len(samples))**0.5 if samples else 0.0

    def pcm_to_wav(pcm):
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(bytes(pcm))
        return buf.getvalue()

    try:
        while True:
            data = await ws.receive()
            if "text" in data:
                try:
                    msg = json.loads(data["text"])
                    if msg.get("type") == "config":
                        language = msg.get("language", "hu")
                    elif msg.get("type") == "stop":
                        break
                except Exception:
                    pass
                continue
            if "bytes" in data:
                chunk = data["bytes"]
                pcm_buffer.extend(chunk)
                energy = rms_energy(chunk)
                if energy >= SILENCE_THRESHOLD:
                    silence_frames = 0
                else:
                    silence_frames += len(chunk)//FRAME_SIZE + 1
                if silence_frames >= SILENCE_FRAMES_LIMIT and len(pcm_buffer) >= CHUNK_MIN_BYTES:
                    wav = pcm_to_wav(pcm_buffer)
                    try:
                        text, _ = await service.transcribe_audio(wav, language, "parakeet")
                        if text:
                            segment_count += 1
                            await ws.send_json({"type": "final", "text": text, "segment": segment_count})
                    except Exception:
                        pass
                    pcm_buffer.clear()
                    silence_frames = 0
    except WebSocketDisconnect:
        logger.info("[LiveASR] WebSocket disconnected")
    except Exception as e:
        logger.error(f"[LiveASR] Error: {e}")
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
