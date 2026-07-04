"""Chat service — meeting-aware Q&A with LiteLLM routing."""

from __future__ import annotations

from meetings.service import meeting_service
from shared.litellm_client import ask_meeting_context


class ChatService:
    """Meeting-aware Q&A service."""

    async def answer_question(
        self, meeting_id: str, question: str, model: str = "openrouter-default"
    ) -> dict:
        """Answer a question about a meeting using LiteLLM routing."""
        meeting = await meeting_service.get_meeting(meeting_id)
        if not meeting:
            return {"answer": "Meeting not found", "meeting_id": meeting_id, "model_used": "none"}

        try:
            answer = await ask_meeting_context(
                meeting_data=meeting,
                question=question,
                model=model,
            )
        except Exception as e:
            answer = f"Error: {str(e)}"

        return {
            "answer": answer,
            "meeting_id": meeting_id,
            "model_used": model,
        }


chat_service = ChatService()
