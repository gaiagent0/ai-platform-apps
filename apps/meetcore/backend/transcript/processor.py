"""Audio preprocessor — noise reduction, resampling, VAD."""

from __future__ import annotations

import io
import wave
from pathlib import Path
from typing import Optional

import numpy as np


class AudioProcessor:
    """Audio preprocessing pipeline."""

    TARGET_SAMPLE_RATE = 16000

    def read_wav(self, path: str | Path) -> tuple[np.ndarray, int]:
        """Read a WAV file and return (audio_array, sample_rate)."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        with wave.open(str(path), "rb") as wf:
            sample_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

        return audio, sample_rate

    def resample(self, audio: np.ndarray, orig_rate: int, target_rate: int = TARGET_SAMPLE_RATE) -> np.ndarray:
        """Resample audio to target sample rate."""
        if orig_rate == target_rate:
            return audio
        ratio = target_rate / orig_rate
        new_len = int(len(audio) * ratio)
        return np.interp(
            np.linspace(0, len(audio) - 1, new_len),
            np.arange(len(audio)),
            audio,
        )

    def normalize(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range."""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return audio / max_val
        return audio

    def preprocess(self, path: str | Path) -> np.ndarray:
        """Full preprocessing: read → resample → normalize."""
        audio, sample_rate = self.read_wav(path)
        audio = self.resample(audio, sample_rate)
        audio = self.normalize(audio)
        return audio


processor = AudioProcessor()
