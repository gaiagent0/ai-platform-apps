"""
meetings/router.py — REST API endpoints for meetings.
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from . import service
from .schemas import MeetingCreate, MeetingDetail, MeetingList, MeetingSummary, MeetingUpdate

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.get("", response_model=MeetingList)
async def list_meetings(session: AsyncSession = Depends(get_session)):
    meetings, total = await service.list_meetings(session)
    return MeetingList(meetings=meetings, total=total)


@router.post("", response_model=MeetingSummary, status_code=201)
async def create_meeting(
    req: MeetingCreate,
    session: AsyncSession = Depends(get_session),
):
    return await service.create_meeting(session, req.title)


@router.get("/{meeting_id}", response_model=MeetingDetail)
async def get_meeting(
    meeting_id: str,
    session: AsyncSession = Depends(get_session),
):
    meeting = await service.get_meeting_detail(session, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail=f"Meeting '{meeting_id}' not found")
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingSummary)
async def update_meeting(
    meeting_id: str,
    req: MeetingUpdate,
    session: AsyncSession = Depends(get_session),
):
    if not req.title:
        raise HTTPException(status_code=400, detail="Title is required")
    meeting = await service.update_meeting(session, meeting_id, req.title)
    if not meeting:
        raise HTTPException(status_code=404, detail=f"Meeting '{meeting_id}' not found")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(
    meeting_id: str,
    session: AsyncSession = Depends(get_session),
):
    ok = await service.delete_meeting(session, meeting_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Meeting '{meeting_id}' not found")


@router.delete("/{meeting_id}/force", status_code=200)
async def delete_meeting_force(
    meeting_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Delete meeting with 200 response (for frontend compatibility)."""
    ok = await service.delete_meeting(session, meeting_id)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Meeting '{meeting_id}' not found")
    return {"success": True, "deleted_id": meeting_id}
