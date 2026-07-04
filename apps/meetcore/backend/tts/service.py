"""TTS service — Piper TTS integration (async)."""

from __future__ import annotations

import asyncio
import base64
import shutil
import tempfile
from pathlib import Path

from core.config import settings


class TTSService:
    """Text-to-speech service using Piper TTS."""

    async def synthesize(
        self, text: str, voice: str = "hu_HU-dfpros-medium", speed: float = 1.0
    ) -> bytes:
        """Synthesize speech from text using Piper TTS (async)."""
        piper_path = settings.piper_executable or "piper"

        # Check if piper binary exists
        if not shutil.which(piper_path):
            raise FileNotFoundError(
                f"Piper TTS binary not found at '{piper_path}'. "
                f"Install Piper: https://github.com/rhasspy/piper"
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            length_scale = 1.0 / speed if speed > 0 else 1.0
            proc = await asyncio.create_subprocess_exec(
                piper_path,
                "--model", voice,
                "--length-scale", str(length_scale),
                "--output_file", tmp_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate(input=text.encode("utf-8"))

            audio_path = Path(tmp_path)
            if audio_path.exists():
                return audio_path.read_bytes()
            raise RuntimeError("Piper TTS failed to produce output")

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def synthesize_base64(
        self, text: str, voice: str = "hu_HU-dfpros-medium", speed: float = 1.0
    ) -> str:
        """Synthesize speech and return base64-encoded audio."""
        audio = await self.synthesize(text, voice=voice, speed=speed)
        return base64.b64encode(audio).decode("utf-8")


tts_service = TTSService()
