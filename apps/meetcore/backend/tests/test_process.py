"""Tests for the process meeting endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from main import app


@pytest.mark.anyio
async def test_process_meeting_returns_processing():
    """POST /{id}/process should return 202 with status 'processing'."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create a meeting first
        resp = await client.post("/api/meetings/", data={"title": "ProcessTest", "language": "hu"})
        assert resp.status_code == 201
        meeting_id = resp.json()["id"]

        # Process it
        resp = await client.post(f"/api/meetings/{meeting_id}/process")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"
        assert data["meeting_id"] == meeting_id


@pytest.mark.anyio
async def test_process_meeting_404_for_missing():
    """POST /nonexistent/process should return 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/meetings/nonexistent-id/process")
        assert resp.status_code == 404


@pytest.mark.anyio
async def test_cleanup_stale_meetings():
    """POST /cleanup-stale should clean stale jobs."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/meetings/cleanup-stale", params={"max_minutes": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "cleaned" in data
        assert "max_minutes" in data
