"""MCP Server wrapper — exposes MeetCore endpoints as MCP tools."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from core.config import settings
from meetings.service import meeting_service
from transcript.service import transcript_service
from chat.service import chat_service

# Create MCP server instance
mcp = FastMCP(
    "MeetCore",
    port=settings.mcp_port,
    instructions="""
    MeetCore — Meeting assistant MCP tools.
    Record, transcribe, summarize, and ask questions about meetings.
    """,
)


@mcp.tool()
async def record_meeting(title: str = "", language: str = "hu") -> str:
    """Create a new meeting recording session."""
    meeting = await meeting_service.create_meeting(title=title, language=language)
    return json.dumps(meeting, ensure_ascii=False)


@mcp.tool()
async def transcribe_audio(audio_path: str, language: str = "hu") -> str:
    """Transcribe an audio file."""
    text = await transcript_service.transcribe_file(audio_path, language=language)
    return text


@mcp.tool()
async def list_meetings() -> str:
    """List all recorded meetings."""
    meetings = await meeting_service.list_meetings()
    if not meetings:
        return "Nincsenek meetingek."
    return json.dumps(meetings, ensure_ascii=False, indent=2)


@mcp.tool()
async def get_meeting_context(meeting_id: str, question: str) -> str:
    """Ask a question about a meeting's content."""
    return await chat_service.answer_question(meeting_id, question)


@mcp.tool()
async def get_meeting_info(meeting_id: str) -> str:
    """Get full meeting details."""
    meeting = await meeting_service.get_meeting(meeting_id)
    if meeting is None:
        return "Meeting nem található."
    return json.dumps(meeting, ensure_ascii=False, indent=2)


def run_mcp_server() -> None:
    """Run the MCP server."""
    mcp.run()
