"""MCP Server wrapper — exposes MeetCore endpoints as MCP tools.

This allows Open WebUI (and other MCP clients) to interact with
MeetCore directly as MCP tools.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .config import settings
from ..meetings.service import meeting_service
from ..transcript.service import transcript_service
from ..chat.service import chat_service
from ..shared.geniex_client import summarize_text

# Create MCP server instance
mcp = FastMCP(
    "MeetCore",
    port=settings.mcp_port,
    instructions="""
    MeetCore — Meeting assistant tools.
    Record, transcribe, summarize, and ask questions about meetings.
    """,
)


@mcp.tool()
async def record_meeting(title: str = "", language: str = "hu") -> str:
    """Create a new meeting recording session."""
    meeting = await meeting_service.create_meeting(title=title, language=language)
    return json.dumps({
        "meeting_id": meeting.id,
        "title": meeting.title,
        "status": meeting.status.value,
        "message": f"Meeting '{meeting.title}' létrehozva. Tölts fel hangfájlt a feldolgozáshoz.",
    }, ensure_ascii=False)


@mcp.tool()
async def transcribe_audio(audio_path: str, language: str = "hu") -> str:
    """Transcribe an audio file."""
    text = await transcript_service.transcribe_file(audio_path, language=language)
    return text


@mcp.tool()
async def summarize_meeting(meeting_id: str) -> str:
    """Summarize a meeting by its ID."""
    meeting = await meeting_service.get_meeting(meeting_id)
    if meeting is None:
        return "Meeting nem található."
    if not meeting.transcript:
        return "A meeting még nincs átírva. Először tölts fel hangfájlt."
    if meeting.summary:
        return meeting.summary

    summary = await summarize_text(meeting.transcript, language=meeting.language)
    storage = meeting_service._get_storage() if hasattr(meeting_service, '_get_storage') else None
    await meeting_service.process_audio(meeting_id, meeting.file_path or "")
    return summary


@mcp.tool()
async def get_meeting_context(meeting_id: str, question: str) -> str:
    """Ask a question about a meeting's content."""
    return await chat_service.answer_question(meeting_id, question)


@mcp.tool()
async def list_meetings() -> str:
    """List all recorded meetings."""
    meetings = await meeting_service.list_meetings()
    if not meetings:
        return "Nincsenek meetingek."
    result = []
    for m in meetings:
        result.append({
            "id": m.id,
            "title": m.title,
            "status": m.status.value,
            "created": m.created_at.isoformat(),
            "has_transcript": m.transcript is not None,
            "has_summary": m.summary is not None,
        })
    return json.dumps(result, ensure_ascii=False, indent=2)


def run_mcp_server() -> None:
    """Run the MCP server."""
    mcp.run()
