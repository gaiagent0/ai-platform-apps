"""SQLAlchemy ORM models for MeetCore."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Meeting(Base):
    """Meeting record."""

    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    status: Mapped[str] = mapped_column(String(20), default="recording")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    meeting_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)

    # Relationships
    transcript_chunks: Mapped[List["TranscriptChunk"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    summary_processes: Mapped[List["SummaryProcess"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )
    transcripts: Mapped[List["Transcript"]] = relationship(
        back_populates="meeting", cascade="all, delete-orphan"
    )


class TranscriptChunk(Base):
    """Raw transcript chunks from ASR."""

    __tablename__ = "transcript_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    transcript_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="transcript_chunks")


class SummaryProcess(Base):
    """AI-generated summaries."""

    __tablename__ = "summary_processes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="summary_processes")

    def get_result_dict(self) -> Optional[dict]:
        """Parse result_json into a dict."""
        import json
        if self.result_json:
            try:
                return json.loads(self.result_json)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def get_metadata_dict(self) -> dict:
        """Return metadata about the summary."""
        return {
            "status": self.status,
            "model_used": self.model_used,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Transcript(Base):
    """Processed/transcribed segments."""

    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    meeting_id: Mapped[str] = mapped_column(ForeignKey("meetings.id"))
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    audio_start_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    audio_end_time: Mapped[Optional[float]] = mapped_column(nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="transcripts")
