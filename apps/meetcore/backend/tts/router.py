"""TTS API router."""

from __future__ import annotations

from fastapi import APIRouter, Form

from .models import TTSRequest, TTSResponse
from .service import tts_service

router = APIRouter(prefix="/api/tts", tags=["tts"])


@router.post("/", response_model=TTSResponse)
async def synthesize_speech(
    text: str = Form(...),
    voice: str = Form("hu_HU-dfpros-medium"),
    speed: float = Form(1.0),
):
    """Synthesize speech from text."""
    audio_b64 = await tts_service.synthesize_base64(text, voice, speed)
    return TTSResponse(audio_base64=audio_b64)
