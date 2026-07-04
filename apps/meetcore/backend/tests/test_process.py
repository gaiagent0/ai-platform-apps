"""Tests for the process meeting endpoint."""

import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.fixture
async def created_meeting():
    """Create a meeting and yield its ID, then delete it after the test."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/meetings/", data={"title": "TestCleanup", "language": "hu"})
        assert resp.status_code == 201
        meeting_id = resp.json()["id"]
        yield meeting_id, client
        await client.delete(f"/api/meetings/{meeting_id}")


@pytest.mark.anyio
async def test_process_meeting_returns_processing(created_meeting):
    """POST /{id}/process should immediately return status 'processing'."""
    meeting_id, client = created_meeting
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
    """POST /cleanup-stale should return cleaned count or 401 if auth required."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/meetings/cleanup-stale", params={"max_minutes": 0})
        assert resp.status_code in (200, 401)
        if resp.status_code == 200:
            data = resp.json()
            assert "cleaned" in data
            assert "max_minutes" in data
