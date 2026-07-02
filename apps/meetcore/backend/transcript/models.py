"""Transcription data models."""

from __future__ import annotations

from pydantic import BaseModel


class Segment(BaseModel):
    start: float
    end: float
    text: str
    confidence: float = 0.0
    speaker: str | None = None


class TranscriptionResult(BaseModel):
    text: str
    segments: list[Segment] = []
    language: str = "hu"
    duration_seconds: float = 0.0
