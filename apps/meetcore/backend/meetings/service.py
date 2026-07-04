"""Meeting service - orchestrates meetings using DB-backed repository."""

from __future__ import annotations
import subprocess
import tempfile

import json
from pathlib import Path
from typing import Any, Callable, Optional

import core.db as db_module
from core.config import settings
from .repository import (
    get_meeting_with_details as repo_get_details,
    create_meeting as repo_create,
    get_meeting as repo_get,
    get_all_meetings as repo_list,
    update_meeting as repo_update,
    update_meeting_status as repo_update_status,
    delete_meeting as repo_delete,
    create_transcript_chunk as repo_create_transcript,
    create_summary_process as repo_create_summary,
)


def _meeting_to_dict(meeting) -> dict:
    """Convert a Meeting ORM object to a serializable dict."""
    return {
        "id": meeting.id,
        "title": meeting.title,
        "status": meeting.status,
        "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        "duration_seconds": meeting.duration_seconds or 0,
    }


class MeetingService:
    """High-level meeting orchestration with DB persistence."""

    def _session(self):
        return db_module.async_session_factory()

    async def _write(self, fn: Callable) -> Any:
        session = self._session()
        try:
            result = await fn(session)
            await session.commit()
            return result
        except (json.JSONDecodeError, ValueError, OSError, RuntimeError) as exc:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def _read(self, fn: Callable) -> Any:
        session = self._session()
        try:
            return await fn(session)
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def create_meeting(self, title: str = "", language: str = "hu") -> dict:
        meeting = await self._write(lambda s: repo_create(s, title=title))
        return {
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "created_at": meeting.created_at.isoformat() if meeting.created_at else None,
        }

    async def get_meeting(self, meeting_id: str) -> Optional[dict]:
        meeting = await self._read(lambda s: repo_get(s, meeting_id))
        if not meeting:
            return None
        return _meeting_to_dict(meeting)

    async def get_meeting_details(self, meeting_id: str) -> Optional[dict]:
        """Get full meeting details including transcript, summary, action_items, topics."""
        details = await self._read(lambda s: repo_get_details(s, meeting_id))
        if details:
            return details
        # Fallback: try basic fields
        meeting = await self._read(lambda s: repo_get(s, meeting_id))
        if not meeting:
            return None
        return _meeting_to_dict(meeting)

    async def list_meetings(self) -> list[dict]:
        meetings = await self._read(repo_list)
        return [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "duration_seconds": m.duration_seconds or 0,
                "has_transcript": bool(m.transcript_chunks),
                "has_summary": bool(m.summary_processes),
            }
            for m in meetings
        ]

    async def update_meeting_status(self, meeting_id: str, status: str) -> Optional[dict]:
        result = await self._write(lambda s: repo_update_status(s, meeting_id, status))
        if result:
            return {"id": meeting_id, "status": status, "updated": True}
        return None

    async def delete_meeting(self, meeting_id: str) -> bool:
        return await self._write(lambda s: repo_delete(s, meeting_id))

    async def save_recording(self, meeting_id: str, audio_data: bytes) -> bool:
        try:
            recordings_dir = Path(settings.recordings_dir or "/data/recordings")
            recordings_dir.mkdir(parents=True, exist_ok=True)
            wav_path = recordings_dir / f"{meeting_id}.wav"
            # Check if the data is already WAV (starts with RIFF header)
            if audio_data[:4] == b"RIFF":
                wav_path.write_bytes(audio_data)
            else:
                # Non-WAV format (MP3, OGG, etc.) -> convert with ffmpeg
                with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                try:
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", tmp_path,
                         "-ar", "16000", "-ac", "1", str(wav_path)],
                        check=True, capture_output=True, timeout=60,
                    )
                finally:
                    import os
                    os.unlink(tmp_path)
            return True
        except OSError as exc:
            raise RuntimeError(f"Failed to save recording: {exc}") from exc

    async def process_meeting(self, meeting_id: str) -> dict:
        """Process a meeting: transcribe audio then summarize with LLM."""
        meeting = await self.get_meeting(meeting_id)
        if not meeting:
            raise ValueError(f"Meeting {meeting_id} not found")

        # --- Step 1: Transcribe ---
        await self.update_meeting_status(meeting_id, "transcribing")
        recordings_dir = Path(settings.recordings_dir or "/data/recordings")
        file_path = recordings_dir / f"{meeting_id}.wav"
        if not file_path.exists():
            raise FileNotFoundError(f"Recording not found: {file_path}")

        from transcript.service import TranscriptService
        ts = TranscriptService()
        result = await ts.transcribe(
            audio_path=str(file_path),
            language=settings.whisper_language,
        )
        transcript_text = result.text
        if not transcript_text or not transcript_text.strip():
            await self.update_meeting_status(meeting_id, "error")
            raise ValueError("Transcription produced empty result")
        # Save transcript chunk to DB
        await self._write(
            lambda s: repo_create_transcript(s, meeting_id, transcript_text)
        )
        await self.update_meeting_status(meeting_id, "transcribed")


        # --- Step 2: Summarize with LLM ---
        await self.update_meeting_status(meeting_id, "summarizing")
        from shared.litellm_client import chat_completion

        summary_prompt = (
            "You are a meeting assistant. Analyze the following meeting transcript "
            "and provide:\n"
            "1. A concise summary (2-3 paragraphs)\n"
            "2. A list of action items (if any)\n"
            "3. A list of key topics discussed\n\n"
            'Respond in JSON format: {"summary": "...", "action_items": ["..."], "topics": ["..."]}\n\n'
        )
        summary_prompt += f"Transcript:\n{transcript_text}"

        llm_response = ""
        try:
            llm_response = await chat_completion(
                messages=[{"role": "user", "content": summary_prompt}],
            )
            parsed = json.loads(llm_response)
            summary_text = parsed.get("summary", "")
            action_items = parsed.get("action_items", [])
            topics = parsed.get("topics", [])
        except Exception:
            summary_text = llm_response if isinstance(llm_response, str) else str(llm_response)
            action_items = []
            topics = []

        # Save summary to DB
        summary_result = {
            "summary": summary_text,
            "action_items": action_items,
            "topics": topics,
        }
        await self._write(
            lambda s: repo_create_summary(s, meeting_id, summary_result, model_used=settings.litellm_model)
        )
        await self.update_meeting_status(meeting_id, "completed")

        return {
            "meeting_id": meeting_id,
            "status": "completed",
            "transcript_length": len(transcript_text),
            "summary_length": len(summary_text),
            "action_items_count": len(action_items),
            "topics_count": len(topics),
        }


meeting_service = MeetingService()
