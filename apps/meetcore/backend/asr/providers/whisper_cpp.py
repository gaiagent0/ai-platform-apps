"""whisper.cpp based ASR."""
import asyncio, logging, subprocess, tempfile, os
from pathlib import Path

logger = logging.getLogger(__name__)

class WhisperCPPASRProvider:
    @property
    def name(self):
        return "whisper"

    async def transcribe(self, audio_bytes: bytes, language: str = "hu", content_type: str = "audio/webm") -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_bytes, language)

    def _transcribe_sync(self, audio_bytes: bytes, language: str) -> str:
        exe = os.getenv("MEETCORE_WHISPER_CPP_EXE", "whisper-cli.exe")
        model = os.getenv("MEETCORE_WHISPER_CPP_MODEL", "models/ggml-base.bin")
        if not Path(exe).exists():
            raise FileNotFoundError(f"whisper-cli.exe not found: {exe}")
        if not Path(model).exists():
            raise FileNotFoundError(f"Whisper model not found: {model}")
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.write(audio_bytes)
        tmp.close()
        try:
            result = subprocess.run([exe, "-m", model, "-f", tmp.name, "--language", language,
                                      "--no-timestamps", "-otxt"], capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                raise RuntimeError(f"whisper-cli error: {result.stderr[:300]}")
            txt_path = tmp.name + ".txt"
            if Path(txt_path).exists():
                t = Path(txt_path).read_text(encoding="utf-8", errors="replace").strip()
                Path(txt_path).unlink(missing_ok=True)
                return t
            return result.stdout.strip()
        finally:
            Path(tmp.name).unlink(missing_ok=True)

    async def health(self):
        exe = os.getenv("MEETCORE_WHISPER_CPP_EXE", "whisper-cli.exe")
        model = os.getenv("MEETCORE_WHISPER_CPP_MODEL", "models/ggml-base.bin")
        return {"online": Path(exe).exists() and Path(model).exists(), "exe": Path(exe).exists(), "model": Path(model).exists()}
