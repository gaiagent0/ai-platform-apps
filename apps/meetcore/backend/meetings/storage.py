"""Meeting storage — in-memory with file-based persistence."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from .models import Meeting, MeetingStatus
from ..shared.config import settings


class MeetingStorage:
    """Manages meeting records with JSON file persistence."""

    def __init__(self) -> None:
        self._meetings: dict[str, Meeting] = {}
        self._storage_path = Path(settings.recordings_dir) / "meetings.json"
        self._load()

    def _load(self) -> None:
        """Load meetings from disk."""
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text())
                for item in data:
                    m = Meeting(**item)
                    self._meetings[m.id] = m
            except (json.JSONDecodeError, KeyError):
                pass

    def _save(self) -> None:
        """Persist meetings to disk."""
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = [m.model_dump(mode="json") for m in self._meetings.values()]
        self._storage_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def create(self, meeting: Meeting) -> Meeting:
        self._meetings[meeting.id] = meeting
        self._save()
        return meeting

    def get(self, meeting_id: str) -> Optional[Meeting]:
        return self._meetings.get(meeting_id)

    def list_all(self) -> list[Meeting]:
        return sorted(
            self._meetings.values(),
            key=lambda m: m.created_at,
            reverse=True,
        )

    def update(self, meeting_id: str, **kwargs) -> Optional[Meeting]:
        meeting = self._meetings.get(meeting_id)
        if meeting is None:
            return None
        for key, value in kwargs.items():
            if hasattr(meeting, key):
                setattr(meeting, key, value)
        meeting.updated_at = datetime.now()
        self._save()
        return meeting

    def delete(self, meeting_id: str) -> bool:
        if meeting_id in self._meetings:
            del self._meetings[meeting_id]
            self._save()
            return True
        return False

    def update_status(self, meeting_id: str, status: MeetingStatus) -> Optional[Meeting]:
        return self.update(meeting_id, status=status)

    def set_transcript(self, meeting_id: str, transcript: str) -> Optional[Meeting]:
        return self.update(
            meeting_id,
            transcript=transcript,
            status=MeetingStatus.TRANSCRIBED,
        )

    def set_summary(self, meeting_id: str, summary: str, action_items: list[str] | None = None, topics: list[str] | None = None) -> Optional[Meeting]:
        kwargs: dict = {
            "summary": summary,
            "status": MeetingStatus.SUMMARIZED,
        }
        if action_items is not None:
            kwargs["action_items"] = action_items
        if topics is not None:
            kwargs["topics"] = topics
        return self.update(meeting_id, **kwargs)


# Singleton instance
storage = MeetingStorage()
