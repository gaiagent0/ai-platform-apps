"""GenieX SDK client wrapper — OpenAI-compatible NPU inference.

GenieX provides an OpenAI-compatible API endpoint running on the
Snapdragon X Elite NPU. This client wraps the openai SDK for
structured LLM calls with proper error handling.
"""

from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from .config import settings


_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    """Get or create the GenieX OpenAI-compatible client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.geniex_base_url,
            api_key=settings.geniex_api_key,
        )
    return _client


async def generate_text(
    prompt: str,
    system_prompt: str | None = None,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Generate text using the local GenieX NPU model."""
    client = get_client()
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=settings.geniex_model,
        messages=messages,  # type: ignore[arg-type]
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


async def summarize_text(text: str, language: str = "hu") -> str:
    """Summarize transcribed text using GenieX NPU."""
    system_prompt = (
        f"Te egy meeting összefoglaló asszisztens vagy. "
        f"A feladatod, hogy tömör, strukturált összefoglalót készíts a megadott "
        f"átiratból {language} nyelven. "
        f"Kiemelt pontok: fő témák, döntések, teendők (action items)."
    )
    prompt = f"Készíts strukturált összefoglalót az alábbi meeting átiratból:\n\n{text}"
    return await generate_text(prompt=prompt, system_prompt=system_prompt)
