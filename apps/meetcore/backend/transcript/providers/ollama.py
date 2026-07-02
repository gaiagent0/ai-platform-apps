"""Ollama provider."""
import json, logging
from typing import Optional
import httpx
from core.config import settings
from .base import TranscriptProvider, ChunkStartCB, ChunkDoneCB, ChunkErrorCB
from ..prompts import build_extraction_prompts, text_to_summary, get_model_family

logger = logging.getLogger(__name__)

class OllamaProvider(TranscriptProvider):
    @property
    def name(self) -> str:
        return "ollama"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    async def summarize(self, text, model=None, language="hu", custom_prompt="",
                        on_chunk_start=None, on_chunk_done=None, on_chunk_error=None):
        model = model or settings.ollama_model or "qwen2.5:7b"
        timeout = settings.ollama_timeout
        chunk_size, overlap = 2000, 200
        step = chunk_size - overlap
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
        all_json = []
        for i, chunk in enumerate(chunks):
            if on_chunk_start:
                await on_chunk_start(i, len(chunks), len(chunk))
            try:
                sys_p, usr_p = build_extraction_prompts(chunk, model_name=model, language=language)
                family = get_model_family(model)
                temp = 0.6 if family == "reasoning" else 0.2
                try:
                    from ollama import AsyncClient
                    client = AsyncClient(host=settings.ollama_host)
                    msgs = []
                    if sys_p:
                        msgs.append({"role": "system", "content": sys_p})
                    msgs.append({"role": "user", "content": usr_p})
                    response = await client.chat(model=model, messages=msgs,
                        options={"temperature": temp, "num_ctx": 4096, "num_predict": 1024})
                    raw = response["message"]["content"]
                except ImportError:
                    url = f"{settings.ollama_host.rstrip('/')}/v1/chat/completions"
                    msgs = []
                    if sys_p:
                        msgs.append({"role": "system", "content": sys_p})
                    msgs.append({"role": "user", "content": usr_p})
                    async with httpx.AsyncClient(timeout=timeout) as c:
                        r = await c.post(url, json={"model": model, "messages": msgs, "temperature": temp, "max_tokens": 1024})
                        r.raise_for_status()
                        raw = r.json()["choices"][0]["message"]["content"]
                result = text_to_summary(raw, chunk_index=i)
                rj = json.dumps(result, ensure_ascii=False)
                all_json.append(rj)
                if on_chunk_done:
                    await on_chunk_done(i, len(chunks), rj)
            except Exception as e:
                logger.error(f"[Ollama] Chunk {i+1} error: {e}")
                if on_chunk_error:
                    await on_chunk_error(i, str(e))
        return len(chunks), all_json
    
    async def health(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(f"{settings.ollama_host}/api/tags")
                if r.status_code == 200:
                    models = [m["name"] for m in r.json().get("models",[])]
                    return {"online": True, "models": models, "url": settings.ollama_host}
        except Exception as e:
            return {"online": False, "error": str(e), "url": settings.ollama_host}
        return {"online": False, "url": settings.ollama_host}
