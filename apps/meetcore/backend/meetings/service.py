"""
meetings/service.py — Business logic for meetings.
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from . import repository
from .schemas import MeetingSummary, MeetingDetail


async def list_meetings(session: AsyncSession) -> tuple[List[MeetingSummary], int]:
    meetings = await repository.get_all_meetings(session)
    summaries = [
        MeetingSummary(
            id=m.id,
            title=m.title,
            created_at=m.created_at,
            updated_at=m.updated_at,
        ) for m in meetings
    ]
    return summaries, len(summaries)


async def get_meeting_detail(session: AsyncSession, meeting_id: str) -> Optional[MeetingDetail]:
    data = await repository.get_meeting_with_details(session, meeting_id)
    if not data:
        return None
    return MeetingDetail(**data)


async def create_meeting(session: AsyncSession, title: str) -> MeetingSummary:
    meeting = await repository.create_meeting(session, title)
    return MeetingSummary(
        id=meeting.id,
        title=meeting.title,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


async def update_meeting(
    session: AsyncSession, meeting_id: str, title: str
) -> Optional[MeetingSummary]:
    meeting = await repository.update_meeting(session, meeting_id, title=title)
    if not meeting:
        return None
    return MeetingSummary(
        id=meeting.id,
        title=meeting.title,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


async def delete_meeting(session: AsyncSession, meeting_id: str) -> bool:
    return await repository.delete_meeting(session, meeting_id)
