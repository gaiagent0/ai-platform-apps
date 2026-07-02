"""LiteLLM gateway client — routes cloud LLM calls through LiteLLM.

LiteLLM provides a unified OpenAI-compatible API gateway with
Langfuse tracing, load balancing, and failover.
"""

from __future__ import annotations

from openai import AsyncOpenAI

from .config import settings


_client: AsyncOpenAI | None = None


def get_litellm_client() -> AsyncOpenAI:
    """Get or create the LiteLLM OpenAI-compatible client."""
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.litellm_base_url,
            api_key=settings.litellm_api_key or "sk-not-set",
        )
    return _client


async def chat_completion(
    messages: list[dict[str, str]],
    model: str = "openrouter-default",
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    """Send a chat completion request through the LiteLLM gateway."""
    client = get_litellm_client()
    response = await client.chat.completions.create(
        model=model,
        messages=messages,  # type: ignore[arg-type]
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


async def ask_meeting_context(
    question: str,
    transcript: str,
    summary: str | None = None,
    model: str = "openrouter-default",
) -> str:
    """Answer a question about a meeting using the LiteLLM gateway."""
    context = f"Meeting átirat:\n{transcript}\n"
    if summary:
        context += f"\nÖsszefoglaló:\n{summary}\n"

    system_prompt = (
        "Te egy meeting-asszisztens vagy. Válaszolj a kérdésre a megadott "
        "meeting átirat és összefoglaló alapján. Ha a válasz nem található "
        "a kontextusban, ezt mondd meg őszintén."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Kontextus:\n{context}\n\nKérdés: {question}"},
    ]
    return await chat_completion(messages, model=model)
