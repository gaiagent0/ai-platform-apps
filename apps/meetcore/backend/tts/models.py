"""TTS data models."""

from __future__ import annotations

from pydantic import BaseModel


class TTSRequest(BaseModel):
    text: str
    voice: str = "hu_HU-dfpros-medium"
    speed: float = 1.0


class TTSResponse(BaseModel):
    audio_base64: str
    format: str = "wav"
    sample_rate: int = 22050
