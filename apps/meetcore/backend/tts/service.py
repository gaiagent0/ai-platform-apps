"""TTS service — Piper TTS integration."""

from __future__ import annotations

import asyncio
import base64
import subprocess
import tempfile
from pathlib import Path

from ..shared.config import settings


class TTSService:
    """Text-to-Speech using Piper."""

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> bytes:
        """Synthesize speech from text using Piper TTS."""
        voice = voice or settings.piper_voice

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name

        try:
            proc = await asyncio.create_subprocess_exec(
                settings.piper_executable,
                "--model", voice,
                "--output-raw",
                "--output-file", output_path,
                "--length-scale", str(1.0 / speed),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate(input=text.encode("utf-8"))

            if proc.returncode != 0:
                raise RuntimeError(f"Piper TTS failed: {stderr.decode()}")

            path = Path(output_path)
            if path.exists():
                return path.read_bytes()
            if stdout:
                return stdout
            raise RuntimeError("No audio output from Piper")

        finally:
            Path(output_path).unlink(missing_ok=True)

    async def synthesize_base64(
        self,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
    ) -> str:
        """Synthesize and return base64-encoded audio."""
        audio = await self.synthesize(text, voice, speed)
        return base64.b64encode(audio).decode("utf-8")


# Singleton
tts_service = TTSService()
