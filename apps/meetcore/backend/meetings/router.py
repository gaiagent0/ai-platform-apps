"""Meetings API router — integrates with DB-backed service."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from .service import meeting_service

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("/")
async def list_meetings():
    """List all meetings."""
    return await meeting_service.list_meetings()


@router.post("/", status_code=201)
async def create_meeting(title: str = Form(""), language: str = Form("hu")):
    """Create a new meeting."""
    return await meeting_service.create_meeting(title=title, language=language)


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    """Get meeting details."""
    meeting = await meeting_service.get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: str):
    """Delete a meeting."""
    deleted = await meeting_service.delete_meeting(meeting_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Meeting not found")


@router.post("/{meeting_id}/upload")
async def upload_recording(
    meeting_id: str,
    file: UploadFile = File(...),
):
    """Upload a recorded audio file for a meeting."""
    audio_data = await file.read()
    success = await meeting_service.save_recording(meeting_id, audio_data)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"status": "uploaded", "meeting_id": meeting_id}

async def _run_process(meeting_id: str) -> None:
    """Background task: transcribe + summarize a meeting."""
    try:
        await meeting_service.process_meeting(meeting_id)
    except Exception as exc:
        await meeting_service.update_meeting_status(meeting_id, "error")
        print(f"[process] {meeting_id} failed: {exc}")


@router.post("/{meeting_id}/process")
async def process_meeting(meeting_id: str, background_tasks: BackgroundTasks):
    """Trigger processing (transcription + summarization) for a meeting."""
    meeting = await meeting_service.get_meeting(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await meeting_service.update_meeting_status(meeting_id, "processing")
    background_tasks.add_task(_run_process, meeting_id)
    return {"status": "processing", "meeting_id": meeting_id}



@router.delete("/{meeting_id}/force")
async def delete_meeting_force(meeting_id: str):
    """Delete meeting with confirmation response."""
    deleted = await meeting_service.delete_meeting(meeting_id)
    return {"success": deleted, "deleted_id": meeting_id}
