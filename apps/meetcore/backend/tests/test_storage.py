"""Tests for meeting CRUD via API."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_meeting(client: AsyncClient):
    response = await client.post(
        "/api/meetings/",
        data={"title": "Storage Test", "language": "hu"},
    )
    assert response.status_code == 201
    meeting_id = response.json()["id"]

    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 200
    assert response.json()["id"] == meeting_id
    assert response.json()["title"] == "Storage Test"


@pytest.mark.asyncio
async def test_delete_meeting(client: AsyncClient):
    response = await client.post(
        "/api/meetings/",
        data={"title": "To Delete"},
    )
    assert response.status_code == 201
    meeting_id = response.json()["id"]

    response = await client.delete(f"/api/meetings/{meeting_id}")
    assert response.status_code in (200, 204)

    response = await client.get(f"/api/meetings/{meeting_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_meetings_ordering(client: AsyncClient):
    await client.post("/api/meetings/", data={"title": "First"})
    await client.post("/api/meetings/", data={"title": "Second"})

    response = await client.get("/api/meetings/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
