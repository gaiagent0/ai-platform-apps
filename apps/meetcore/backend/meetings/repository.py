"""
meetings/repository.py — Database operations for meetings.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import Meeting, Transcript, TranscriptChunk, SummaryProcess


async def create_meeting(
    session: AsyncSession,
    title: str,
    meeting_id: Optional[str] = None,
) -> Meeting:
    meeting = Meeting(
        id=meeting_id or str(uuid.uuid4()),
        title=title or "Untitled Meeting",
    )
    session.add(meeting)
    await session.flush()
    return meeting


async def get_meeting(session: AsyncSession, meeting_id: str) -> Optional[Meeting]:
    result = await session.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()


async def get_all_meetings(session: AsyncSession, limit: int = 50) -> List[Meeting]:
    result = await session.execute(
        select(Meeting)
        .options(
            joinedload(Meeting.transcript_chunks).load_only(TranscriptChunk.id),
            joinedload(Meeting.summary_processes).load_only(SummaryProcess.id),
        )
        .order_by(Meeting.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().unique().all())


async def update_meeting(
    session: AsyncSession,
    meeting_id: str,
    *,
    title: Optional[str] = None,
    status: Optional[str] = None,
    transcript: Optional[str] = None,
    summary: Optional[str] = None,
    action_items: Optional[list] = None,
    topics: Optional[list] = None,
    file_path: Optional[str] = None,
) -> Optional[Meeting]:
    """Update meeting fields (only non-None values are applied)."""
    meeting = await get_meeting(session, meeting_id)
    if not meeting:
        return None
    if title is not None:
        meeting.title = title
    if status is not None:
        meeting.status = status
    if transcript is not None:
        meeting.transcript = transcript
    if summary is not None:
        meeting.summary = summary
    if action_items is not None:
        meeting.action_items = action_items
    if topics is not None:
        meeting.topics = topics
    if file_path is not None:
        meeting.file_path = file_path
    await session.flush()
    return meeting


async def delete_meeting(session: AsyncSession, meeting_id: str) -> bool:
    meeting = await get_meeting(session, meeting_id)
    if not meeting:
        return False
    await session.delete(meeting)
    await session.flush()
    return True


async def get_meeting_with_details(session: AsyncSession, meeting_id: str) -> Optional[dict]:
    """Get meeting with transcripts and summary."""
    meeting = await get_meeting(session, meeting_id)
    if not meeting:
        return None
    
    # Get summary
    result = await session.execute(
        select(SummaryProcess).where(
            SummaryProcess.meeting_id == meeting_id,
            SummaryProcess.status == "COMPLETED",
        )
    )
    summary_process = result.scalar_one_or_none()
    
    # Get transcripts
    result = await session.execute(
        select(Transcript).where(Transcript.meeting_id == meeting_id).order_by(Transcript.timestamp)
    )
    transcripts = list(result.scalars().all())
    
    # Get full transcript from transcript_chunks
    result = await session.execute(
        select(TranscriptChunk).where(TranscriptChunk.meeting_id == meeting_id)
    )
    chunk = result.scalar_one_or_none()
    
    _result_dict = summary_process.get_result_dict() if summary_process else None
    return {
        "id": meeting.id,
        "title": meeting.title,
        "status": meeting.status,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
        "summary": _result_dict,
        "summary_text": (_result_dict or {}).get("summary", "") if _result_dict else None,
        "summary_metadata": summary_process.get_metadata_dict() if summary_process else {},
        "transcripts": [{
            "id": t.id,
            "text": t.transcript,
            "timestamp": t.timestamp,
            "audio_start_time": t.audio_start_time,
            "audio_end_time": t.audio_end_time,
            "duration": t.duration,
        } for t in transcripts],
        "full_transcript": chunk.transcript_text if chunk else None,
    }


async def update_meeting_status(
    session: AsyncSession, meeting_id: str, status: str
) -> Optional[Meeting]:
    """Update meeting status."""
    meeting = await get_meeting(session, meeting_id)
    if not meeting:
        return None
    meeting.status = status
    await session.flush()
    return meeting
