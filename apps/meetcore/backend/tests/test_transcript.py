"""Tests for transcription service."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_transcribe_endpoint_no_file(client: AsyncClient):
    """Transcribe without file returns 422."""
    response = await client.post("/api/transcribe/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_transcribe_endpoint_empty(client: AsyncClient):
    """Transcribe with empty file returns 400."""
    response = await client.post(
        "/api/transcribe/",
        files={"file": ("empty.wav", b"", "audio/wav")},
        data={"language": "hu"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_tts_endpoint(client: AsyncClient):
    """TTS endpoint requires text."""
    response = await client.post("/api/tts/")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_chat_endpoint_no_data(client: AsyncClient):
    """Chat endpoint requires data."""
    response = await client.post("/api/chat/")
    assert response.status_code == 422
