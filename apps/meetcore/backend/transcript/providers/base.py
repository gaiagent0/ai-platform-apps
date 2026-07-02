"""
base.py — Abstract provider interface for transcript summarization.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Awaitable


# Callback types for SSE streaming
ChunkStartCB = Optional[Callable[[int, int, int], Awaitable[None]]]
ChunkDoneCB = Optional[Callable[[int, int, str], Awaitable[None]]]
ChunkErrorCB = Optional[Callable[[int, str], Awaitable[None]]]


class TranscriptProvider(ABC):
    """
    Abstract base class for all transcript summarization providers.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g. 'geniex', 'ollama', 'claude')."""
        pass
    
    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses."""
        pass
    
    @abstractmethod
    async def summarize(
        self,
        text: str,
        model: Optional[str] = None,
        language: str = "hu",
        custom_prompt: str = "",
        on_chunk_start: ChunkStartCB = None,
        on_chunk_done: ChunkDoneCB = None,
        on_chunk_error: ChunkErrorCB = None,
    ) -> tuple[int, list[str]]:
        """
        Summarize a transcript text.
        Returns (total_chunks, list_of_json_results).
        """
        pass
    
    @abstractmethod
    async def health(self) -> dict:
        """Health check for this provider."""
        pass


class ProviderRegistry:
    """Registry of all available providers."""
    
    _providers: dict[str, TranscriptProvider] = {}
    
    @classmethod
    def register(cls, provider: TranscriptProvider) -> None:
        cls._providers[provider.name] = provider
    
    @classmethod
    def get(cls, name: str) -> TranscriptProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: '{name}'. Available: {list(cls._providers.keys())}")
        return cls._providers[name]
    
    @classmethod
    def list(cls) -> list[str]:
        return list(cls._providers.keys())
    
    @classmethod
    async def health_all(cls) -> dict:
        results = {}
        for name, provider in cls._providers.items():
            try:
                results[name] = await provider.health()
            except Exception as e:
                results[name] = {"online": False, "error": str(e)}
        return results
