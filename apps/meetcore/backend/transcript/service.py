"""Transcription service — supports Faster-Whisper and Parakeet ASR."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..shared.config import settings
from .models import Segment, TranscriptionResult
from .processor import processor


class TranscriptService:
    """Speech-to-text transcription service."""

    def __init__(self) -> None:
        self._whisper_model = None
        self._model_loaded = False

    def _load_whisper(self):
        """Lazy-load Faster-Whisper model."""
        if not self._model_loaded:
            from faster_whisper import WhisperModel
            self._whisper_model = WhisperModel(
                model_size_or_path=settings.whisper_model_size,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
            )
            self._model_loaded = True
        return self._whisper_model

    async def transcribe_file(self, audio_path: str, language: str = "hu") -> str:
        """Transcribe an audio file and return the full text."""
        result = await self.transcribe(audio_path, language)
        return result.text

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> TranscriptionResult:
        """Transcribe audio using Faster-Whisper."""
        model = self._load_whisper()
        audio = processor.preprocess(audio_path)

        segments, info = model.transcribe(
            audio,
            language=language or settings.whisper_language,
            beam_size=5,
            vad_filter=True,
        )

        seg_list: list[Segment] = []
        full_text_parts: list[str] = []
        for seg in segments:
            seg_list.append(
                Segment(
                    start=seg.start,
                    end=seg.end,
                    text=seg.text.strip(),
                    confidence=seg.avg_logprob,
                )
            )
            full_text_parts.append(seg.text.strip())

        return TranscriptionResult(
            text=" ".join(full_text_parts),
            segments=seg_list,
            language=info.language if info else language or "hu",
            duration_seconds=info.duration if info else 0.0,
        )

    async def transcribe_parakeet(self, audio_path: str) -> str:
        """Transcribe using Parakeet ASR on NPU (via HTTP API)."""
        import httpx
        audio_path_obj = Path(audio_path)
        if not audio_path_obj.exists():
            return ""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.parakeet_base_url}/asr",
                files={"file": audio_path_obj.read_bytes()},
                timeout=120.0,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("text", "")
        return ""


# Singleton
transcript_service = TranscriptService()
