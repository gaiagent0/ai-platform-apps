"""Chat API router."""

from __future__ import annotations

from fastapi import APIRouter, Form

from .models import ChatResponse
from .service import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat_with_meeting(
    meeting_id: str = Form(...),
    question: str = Form(...),
    model: str = Form("openrouter-default"),
):
    """Ask a question about a meeting."""
    answer = await chat_service.answer_question(
        meeting_id=meeting_id,
        question=question,
        model=model,
    )
    return ChatResponse(answer=answer, meeting_id=meeting_id, model_used=model)
