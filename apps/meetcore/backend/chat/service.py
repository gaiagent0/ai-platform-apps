"""Chat service — meeting-aware Q&A with LiteLLM routing."""

from __future__ import annotations

from typing import Optional

from ..meetings.storage import storage
from ..shared.litellm_client import ask_meeting_context


class ChatService:
    """Meeting-aware chat service."""

    async def answer_question(
        self,
        meeting_id: str,
        question: str,
        model: str = "openrouter-default",
    ) -> str:
        """Answer a question about a meeting."""
        meeting = storage.get(meeting_id)
        if meeting is None:
            return "Meeting nem található."
        if not meeting.transcript:
            return "A meeting még nincs feldolgozva (nincs átirat)."

        return await ask_meeting_context(
            question=question,
            transcript=meeting.transcript,
            summary=meeting.summary,
            model=model,
        )


# Singleton
chat_service = ChatService()
