"""Tests for MCP server."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_mcp_list_meetings():
    """MCP list_meetings tool works."""
    from shared.mcp_server import list_meetings
    from meetings.storage import storage

    # Should not raise
    result = await list_meetings()
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_mcp_record_meeting():
    """MCP record_meeting tool works."""
    from shared.mcp_server import record_meeting

    result = await record_meeting(title="MCP Test Meeting")
    assert isinstance(result, str)
    assert "MCP Test Meeting" in result or "meeting_id" in result
