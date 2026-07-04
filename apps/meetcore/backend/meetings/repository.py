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
    title: Optional[str] = None,
) -> Optional[Meeting]:
    meeting = await get_meeting(session, meeting_id)
    if not meeting:
        return None
    if title is not None:
        meeting.title = title
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
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "created_at": meeting.created_at,
        "updated_at": meeting.updated_at,
        "summary": summary_process.get_result_dict() if summary_process else None,
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
