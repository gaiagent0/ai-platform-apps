"""Chat data models."""

from __future__ import annotations

from pydantic import BaseModel


class ChatRequest(BaseModel):
    meeting_id: str
    question: str
    model: str = "openrouter-default"


class ChatResponse(BaseModel):
    answer: str
    meeting_id: str
    model_used: str
