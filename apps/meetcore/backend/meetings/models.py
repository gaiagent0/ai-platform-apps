"""Meeting data models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MeetingStatus(str, Enum):
    RECORDING = "recording"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    SUMMARIZED = "summarized"
    COMPLETED = "completed"
    FAILED = "failed"


class Meeting(BaseModel):
    id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    title: str = ""
    status: MeetingStatus = MeetingStatus.RECORDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    duration_seconds: int = 0
    file_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    language: str = "hu"


class MeetingCreate(BaseModel):
    title: str = ""
    language: str = "hu"


class MeetingListItem(BaseModel):
    id: str
    title: str
    status: MeetingStatus
    created_at: datetime
    duration_seconds: int
    has_transcript: bool = False
    has_summary: bool = False
