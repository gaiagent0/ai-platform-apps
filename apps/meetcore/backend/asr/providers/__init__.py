"""ASR providers — Parakeet NPU and WhisperCPP."""

from .parakeet import ParakeetASRProvider
from .whisper_cpp import WhisperCPPASRProvider

__all__ = ["ParakeetASRProvider", "WhisperCPPASRProvider"]
