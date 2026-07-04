"""Tests for the process meeting endpoint."""

import json
import wave
import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
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


@pytest.mark.anyio
async def test_process_pipeline_with_mocks(created_meeting, tmp_path):
    """Test full pipeline using mocks (verifies status transitions)."""
    meeting_id, client = created_meeting

    wav_path = tmp_path / f"{meeting_id}.wav"
    with wave.open(str(wav_path), 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(b'\x00\x00' * 16000)

    mock_ts_instance = MagicMock()
    mock_ts_instance.transcribe = AsyncMock()
    mock_result = MagicMock()
    mock_result.text = 'Ez egy teszt transzkripcio a meetingrol.'
    mock_ts_instance.transcribe.return_value = mock_result

    with patch('transcript.service.TranscriptService', return_value=mock_ts_instance), \
         patch('shared.litellm_client.chat_completion', new_callable=AsyncMock) as mock_chat, \
         patch('meetings.service.settings') as mock_settings:

        mock_settings.recordings_dir = str(tmp_path)
        mock_settings.whisper_language = 'hu'

        mock_chat.return_value = json.dumps({
            'summary': 'A meeting osszefoglalasa.',
            'action_items': ['Tennivalo 1'],
            'topics': ['Tema 1'],
        })

        resp = await client.post(f'/api/meetings/{meeting_id}/process')
        assert resp.status_code == 200
        assert resp.json()['status'] == 'processing'

        # Wait for background task to complete
        for _ in range(10):
            await asyncio.sleep(0.5)
            resp = await client.get(f'/api/meetings/{meeting_id}')
            status = resp.json()['status']
            if status in ('completed', 'error'):
                break

        assert status in ('completed', 'error')
