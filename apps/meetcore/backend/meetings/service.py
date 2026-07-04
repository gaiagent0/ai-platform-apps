"""Meeting service — orchestrates meetings using DB-backed repository."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Optional

import core.db as db_module
from core.config import settings
from .repository import (
    create_meeting as repo_create,
    get_meeting as repo_get,
    get_all_meetings as repo_list,
    update_meeting_status as repo_update_status,
    delete_meeting as repo_delete,
)


class MeetingService:
    """High-level meeting orchestration with DB persistence."""

    def _session(self):
        return db_module.async_session_factory()

    async def _write(self, fn: Callable) -> Any:
        """Run a write operation with commit."""
        session = self._session()
        try:
            result = await fn(session)
            await session.commit()
            return result
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def _read(self, fn: Callable) -> Any:
        """Run a read-only operation (no commit)."""
        session = self._session()
        try:
            return await fn(session)
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_meeting(self, title: str = "", language: str = "hu") -> dict:
        meeting = await self._write(lambda s: repo_create(s, title=title))
        return {
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        }

    async def get_meeting(self, meeting_id: str) -> Optional[dict]:
        meeting = await self._read(lambda s: repo_get(s, meeting_id))
        if not meeting:
            return None
        return {
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        }

    async def list_meetings(self) -> list[dict]:
        meetings = await self._read(repo_list)
        return [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "duration_seconds": m.duration_seconds or 0,
                "has_transcript": bool(m.transcript_chunks),
                "has_summary": bool(m.summary_processes),
            }
            for m in meetings
        ]

    async def update_meeting_status(self, meeting_id: str, status: str) -> Optional[dict]:
        result = await self._write(lambda s: repo_update_status(s, meeting_id, status))
        if result:
            return {"id": meeting_id, "status": status, "updated": True}
        return None

    async def delete_meeting(self, meeting_id: str) -> bool:
        return await self._write(lambda s: repo_delete(s, meeting_id))

    async def save_recording(self, meeting_id: str, audio_data: bytes) -> bool:
        try:
            recordings_dir = Path(settings.recordings_dir or "/data/recordings")
            recordings_dir.mkdir(parents=True, exist_ok=True)
            file_path = recordings_dir / f"{meeting_id}.wav"
            file_path.write_bytes(audio_data)
            return True
        except OSError as exc:
            raise RuntimeError(f"Failed to save recording: {exc}") from exc


meeting_service = MeetingService()
