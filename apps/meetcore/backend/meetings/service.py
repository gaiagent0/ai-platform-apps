"""Meeting service — orchestrates meetings using DB-backed repository."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import get_session, init_db
from .models import Meeting, MeetingStatus, MeetingListItem
from .schemas import MeetingSummary, MeetingDetail, MeetingList
from .repository import (
    create_meeting as repo_create,
    get_meeting as repo_get,
    get_all_meetings as repo_list,
    update_meeting as repo_update,
    delete_meeting as repo_delete,
    get_meeting_with_details as repo_detail,
)


class MeetingService:
    """High-level meeting orchestration with DB persistence."""

    async def create_meeting(self, title: str = "", language: str = "hu") -> dict:
        """Create a new meeting in the database."""
        async with get_session() as session:
            meeting = await repo_create(session, title=title)
            return MeetingSummary.model_validate(meeting).model_dump()

    async def get_meeting(self, meeting_id: str) -> Optional[dict]:
        """Get meeting with full details."""
        async with get_session() as session:
            detail = await repo_detail(session, meeting_id)
            if detail is None:
                return None
            return detail

    async def list_meetings(self, limit: int = 50) -> list[dict]:
        """List all meetings."""
        async with get_session() as session:
            meetings = await repo_list(session, limit=limit)
            return [
                {
                    "id": m.id,
                    "title": m.title,
                    "status": "completed" if m.summary else "recorded",
                    "created_at": m.created_at.isoformat() if m.created_at else "",
                    "updated_at": m.updated_at.isoformat() if m.updated_at else "",
                    "duration_seconds": 0,
                    "has_transcript": m.transcript is not None if hasattr(m, 'transcript') else False,
                    "has_summary": m.summary is not None if hasattr(m, 'summary') else False,
                }
                for m in meetings
            ]

    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting."""
        async with get_session() as session:
            return await repo_delete(session, meeting_id)

    async def update_meeting_status(self, meeting_id: str, status: MeetingStatus) -> Optional[dict]:
        """Update meeting status."""
        async with get_session() as session:
            meeting = await repo_update(session, meeting_id, title=status.value)
            if meeting is None:
                return None
            return MeetingSummary.model_validate(meeting).model_dump()

    async def save_recording(
        self,
        meeting_id: str,
        audio_data: bytes,
        filename: str = "recording.wav",
    ) -> bool:
        """Save raw audio recording to disk."""
        recordings_dir = Path(settings.recordings_dir) if hasattr(settings, 'recordings_dir') else Path("/data/recordings")
        recordings_dir.mkdir(parents=True, exist_ok=True)
        file_path = recordings_dir / f"{meeting_id}_{filename}"
        file_path.write_bytes(audio_data)
        return True


# Singleton
meeting_service = MeetingService()
