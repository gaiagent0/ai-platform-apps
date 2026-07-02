"""Tests for meeting storage."""

from __future__ import annotations

from meetings.models import Meeting, MeetingStatus
from meetings.storage import MeetingStorage


def test_storage_create_and_get():
    """Can create and retrieve a meeting."""
    storage = MeetingStorage()
    meeting = Meeting(id="test1", title="Storage Test")
    storage.create(meeting)

    retrieved = storage.get("test1")
    assert retrieved is not None
    assert retrieved.title == "Storage Test"
    assert retrieved.status == MeetingStatus.RECORDING


def test_storage_update():
    """Can update a meeting."""
    storage = MeetingStorage()
    meeting = Meeting(id="test2")
    storage.create(meeting)

    updated = storage.update("test2", title="Updated", duration_seconds=300)
    assert updated is not None
    assert updated.title == "Updated"
    assert updated.duration_seconds == 300


def test_storage_delete():
    """Can delete a meeting."""
    storage = MeetingStorage()
    meeting = Meeting(id="test3")
    storage.create(meeting)

    assert storage.delete("test3") is True
    assert storage.get("test3") is None


def test_storage_list():
    """Can list meetings in reverse chronological order."""
    storage = MeetingStorage()
    m1 = Meeting(id="older")
    m2 = Meeting(id="newer")
    storage.create(m1)
    storage.create(m2)

    meetings = storage.list_all()
    assert len(meetings) == 2
    assert meetings[0].id == "newer"  # Most recent first


def test_storage_set_transcript():
    """Can set transcript and status updates."""
    storage = MeetingStorage()
    meeting = Meeting(id="test4")
    storage.create(meeting)

    storage.set_transcript("test4", "Hello world")
    retrieved = storage.get("test4")
    assert retrieved is not None
    assert retrieved.transcript == "Hello world"
    assert retrieved.status == MeetingStatus.TRANSCRIBED
