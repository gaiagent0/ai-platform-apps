"""
models.py — MeetCore v3
SQLAlchemy ORM models for all domains.
"""

import json
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .db import Base


class Meeting(Base):
    __tablename__ = "meetings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    meeting_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    transcript_chunks: Mapped[List["TranscriptChunk"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    summary_processes: Mapped[List["SummaryProcess"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")
    transcripts: Mapped[List["Transcript"]] = relationship(back_populates="meeting", cascade="all, delete-orphan")


class Transcript(Base):
    __tablename__ = "transcripts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    meeting_id: Mapped[str] = mapped_column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"))
    transcript: Mapped[str] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    audio_start_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    audio_end_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    meeting: Mapped["Meeting"] = relationship(back_populates="transcripts")


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"
    
    meeting_id: Mapped[str] = mapped_column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True)
    meeting_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    transcript_text: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    chunk_size: Mapped[int] = mapped_column(Integer, default=2000)
    overlap: Mapped[int] = mapped_column(Integer, default=200)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    meeting: Mapped["Meeting"] = relationship(back_populates="transcript_chunks")


class SummaryProcess(Base):
    __tablename__ = "summary_processes"
    
    meeting_id: Mapped[str] = mapped_column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    processing_time: Mapped[float] = mapped_column(Float, default=0.0)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    meeting: Mapped["Meeting"] = relationship(back_populates="summary_processes")
    
    def get_result_dict(self) -> dict:
        if self.result:
            try:
                return json.loads(self.result)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def get_metadata_dict(self) -> dict:
        if self.metadata:
            try:
                return json.loads(self.metadata)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}


class ApiKey(Base):
    __tablename__ = "api_keys"
    
    provider: Mapped[str] = mapped_column(String(50), primary_key=True)
    api_key: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AppSetting(Base):
    __tablename__ = "app_settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text)
