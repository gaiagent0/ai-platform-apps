"""Tests for meetings API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Health endpoint returns 200."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "meetcore"


@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient):
    """Can create a new meeting."""
    response = await client.post(
        "/api/meetings/",
        data={"title": "Test Meeting", "language": "hu"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Meeting"
    assert data["status"] == "recording"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient):
    """Can list all meetings."""
    response = await client.get("/api/meetings/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_meeting_not_found(client: AsyncClient):
    """Non-existent meeting returns 404."""
    response = await client.get("/api/meetings/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_meeting(client: AsyncClient):
    """Create a meeting then retrieve it."""
    create_resp = await client.post(
        "/api/meetings/",
        data={"title": "Integration Test", "language": "en"},
    )
    meeting_id = create_resp.json()["id"]

    get_resp = await client.get(f"/api/meetings/{meeting_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["title"] == "Integration Test"
    assert data["language"] == "en"
