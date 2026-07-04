"""Tests for meetings API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "MeetCore"


@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient):
    response = await client.post(
        "/api/meetings/",
        data={"title": "Test Meeting", "language": "hu"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Meeting"
    assert data["status"] == "recording"


@pytest.mark.asyncio
async def test_list_meetings(client: AsyncClient):
    await client.post("/api/meetings/", data={"title": "Meeting A"})
    await client.post("/api/meetings/", data={"title": "Meeting B"})
    response = await client.get("/api/meetings/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_meeting_not_found(client: AsyncClient):
    response = await client.get("/api/meetings/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_meeting_not_found(client: AsyncClient):
    response = await client.delete("/api/meetings/nonexistent")
    assert response.status_code == 404
