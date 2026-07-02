"""ASR service."""
from .providers import ParakeetASRProvider, WhisperCPPASRProvider

_parakeet = ParakeetASRProvider()
_whisper = WhisperCPPASRProvider()

async def transcribe_audio(audio_bytes: bytes, language: str = "hu", backend: str = "auto"):
    if backend == "parakeet":
        text = await _parakeet.transcribe(audio_bytes, language)
        return text, "parakeet"
    if backend == "whisper":
        text = await _whisper.transcribe(audio_bytes, language)
        return text, "whisper"
    try:
        text = await _parakeet.transcribe(audio_bytes, language)
        return text, "parakeet"
    except Exception:
        text = await _whisper.transcribe(audio_bytes, language)
        return text, "whisper"

async def health_all() -> dict:
    return {"parakeet": await _parakeet.health(), "whisper": await _whisper.health()}
