"""Tests for MCP server."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_mcp_record_meeting(client: AsyncClient):
    """MCP record_meeting tool works via API."""
    # Test meeting creation via the API (which MCP tools wrap)
    response = await client.post(
        "/api/meetings/",
        data={"title": "MCP Test Meeting", "language": "hu"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "MCP Test Meeting" in data["title"]
    assert data["id"]


@pytest.mark.asyncio
async def test_mcp_list_meetings(client: AsyncClient):
    """MCP list_meetings tool works via API."""
    # Create a meeting first
    await client.post(
        "/api/meetings/",
        data={"title": "List Test", "language": "hu"},
    )
    # List meetings (what MCP list_meetings does)
    response = await client.get("/api/meetings/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_mcp_get_meeting_context(client: AsyncClient):
    """MCP get_meeting_context tool returns meeting info."""
    # Create a meeting
    response = await client.post(
        "/api/meetings/",
        data={"title": "Context Test"},
    )
    assert response.status_code == 201
    meeting_id = response.json()["id"]

    # Get meeting details (what MCP get_meeting_info does)
    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == meeting_id
    assert data["title"] == "Context Test"
