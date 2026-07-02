"""LiteLLM Gateway provider."""
import json, logging
from typing import Optional
import httpx
from core.config import settings
from .base import TranscriptProvider, ChunkStartCB, ChunkDoneCB, ChunkErrorCB
from ..prompts import build_json_prompts, build_anthropic_prompts

logger = logging.getLogger(__name__)

CLOUD_MODELS = {
    "claude": {"default": "claude-3-5-haiku-20241022", "mode": "anthropic"},
    "groq": {"default": "llama-3.3-70b-versatile", "mode": "openai-json"},
    "openai": {"default": "gpt-4o-mini", "mode": "openai-json"},
    "openrouter": {"default": "meta-llama/llama-3.3-70b-instruct", "mode": "openai-text"},
}

class LiteLLMProvider(TranscriptProvider):
    """Routes all cloud provider calls through LiteLLM gateway."""
    
    @property
    def name(self) -> str:
        return "litellm"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    async def summarize(self, text, model=None, language="hu", custom_prompt="",
                        on_chunk_start=None, on_chunk_done=None, on_chunk_error=None):
        if not model or "/" not in model:
            raise ValueError("Model must be 'provider/model_name', e.g. 'claude/claude-3-5-haiku'")
        provider, actual_model = model.split("/", 1)
        timeout = settings.litellm_timeout
        chunk_size = 8000 if provider in ("openai", "claude") else 6000
        overlap = 400 if provider in ("openai", "claude") else 500
        step = chunk_size - overlap
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
        all_json = []
        base_url = f"{settings.litellm_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.litellm_api_key}", "Content-Type": "application/json"}
        for i, chunk in enumerate(chunks):
            if on_chunk_start:
                await on_chunk_start(i, len(chunks), len(chunk))
            try:
                if provider == "claude":
                    sys_p, usr_p = build_anthropic_prompts(chunk, custom_prompt, language)
                    payload = {"model": model, "messages": [{"role": "user", "content": usr_p}],
                              "max_tokens": 4096, "temperature": 0.3}
                else:
                    sys_p, usr_p = build_json_prompts(chunk, model_name=actual_model, custom_prompt=custom_prompt, language=language)
                    payload = {"model": model, "messages": [
                        {"role": "system", "content": sys_p},
                        {"role": "user", "content": usr_p},
                    ], "temperature": 0.3, "max_tokens": 4096}
                    if provider != "openrouter":
                        payload["response_format"] = {"type": "json_object"}
                async with httpx.AsyncClient(timeout=timeout) as c:
                    resp = await c.post(base_url, headers=headers, json=payload)
                    resp.raise_for_status()
                raw = resp.json()["choices"][0]["message"]["content"]
                all_json.append(raw)
                if on_chunk_done:
                    await on_chunk_done(i, len(chunks), raw)
            except Exception as e:
                logger.error(f"[LiteLLM/{provider}] Chunk {i+1} error: {e}")
                if on_chunk_error:
                    await on_chunk_error(i, str(e))
        return len(chunks), all_json
    
    async def health(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(f"{settings.litellm_base_url.rstrip('/')}/models",
                               headers={"Authorization": f"Bearer {settings.litellm_api_key}"})
                if r.status_code == 200:
                    models = [m.get("id","") for m in r.json().get("data",[])]
                    return {"online": True, "models": models, "url": settings.litellm_base_url}
        except Exception as e:
            return {"online": False, "error": str(e), "url": settings.litellm_base_url}
        return {"online": False, "url": settings.litellm_base_url}
