"""Transcription API router."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from .models import TranscriptionResult
from .service import transcript_service

router = APIRouter(prefix="/api/transcribe", tags=["transcription"])


@router.post("/", response_model=TranscriptionResult)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("hu"),
):
    """Transcribe an uploaded audio file."""
    audio_data = await file.read()
    if not audio_data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    temp_path = f"/tmp/upload_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(audio_data)

    result = await transcript_service.transcribe(temp_path, language=language)
    return result


@router.post("/parakeet")
async def transcribe_parakeet(file: UploadFile = File(...)):
    """Transcribe audio using Parakeet ASR on NPU."""
    audio_data = await file.read()
    temp_path = f"/tmp/upload_parakeet_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(audio_data)

    text = await transcript_service.transcribe_parakeet(temp_path)
    return {"text": text, "engine": "parakeet-npu"}
