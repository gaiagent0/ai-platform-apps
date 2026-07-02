"""
meetings/schemas.py — Pydantic models for meeting data.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class MeetingSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}


class TranscriptData(BaseModel):
    id: str
    text: str
    timestamp: datetime
    audio_start_time: Optional[float] = None
    audio_end_time: Optional[float] = None
    duration: Optional[float] = None


class MeetingDetail(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    meeting_date: Optional[datetime] = None
    transcript: Optional[str] = None
    summary: Optional[dict] = None
    transcripts: List[TranscriptData] = []


class MeetingCreate(BaseModel):
    title: str = Field(default="", max_length=255)
    meeting_date: Optional[datetime] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=255)


class MeetingList(BaseModel):
    meetings: List[MeetingSummary]
    total: int
