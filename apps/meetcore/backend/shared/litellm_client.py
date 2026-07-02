"""LiteLLM gateway client — routes cloud LLM calls through LiteLLM."""

from __future__ import annotations

from openai import AsyncOpenAI

from core.config import settings


_client: AsyncOpenAI | None = None


def get_litellm_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            base_url=settings.litellm_base_url,
            api_key=settings.litellm_api_key or "sk-local",
        )
    return _client


async def chat_completion(
    messages: list[dict[str, str]],
    model: str = "openrouter-default",
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> str:
    client = get_litellm_client()
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
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
    context = f"Meeting átirat:\n{transcript}\n"
    if summary:
        context += f"\nÖsszefoglaló:\n{summary}\n"

    system_prompt = (
        "Te egy meeting-asszisztens vagy. Válaszolj a kérdésre a megadott "
        "meeting átirat és összefoglaló alapján."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Kontextus:\n{context}\n\nKérdés: {question}"},
    ]
    return await chat_completion(messages, model=model)
