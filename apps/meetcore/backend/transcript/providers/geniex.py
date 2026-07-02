"""GenieX Provider -- Qualcomm NPU via GenieX SDK."""
import json, logging
from typing import Optional
import httpx
from core.config import settings
from .base import TranscriptProvider, ChunkStartCB, ChunkDoneCB, ChunkErrorCB
from ..prompts import build_extraction_prompts, text_to_summary, get_model_family

logger = logging.getLogger(__name__)

class GenieXProvider(TranscriptProvider):
    @property
    def name(self) -> str:
        return "geniex"

    @property
    def supports_streaming(self) -> bool:
        return True

    async def _extract_chunk(self, chunk: str, model: str, timeout: float) -> str:
        system_prompt, user_prompt = build_extraction_prompts(chunk, model_name=model)
        family = get_model_family(model)
        num_predict = 512 if family == "npu" else 1024
        temperature = 0.6 if family == "reasoning" else 0.2
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        url = f"{settings.geniex_api_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json={
                "model": model, "messages": messages,
                "temperature": temperature, "max_tokens": num_predict,
            })
            resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    async def summarize(self, text, model=None, language="hu", custom_prompt="",
                        on_chunk_start=None, on_chunk_done=None, on_chunk_error=None):
        model = model or settings.geniex_model
        timeout = settings.geniex_timeout
        chunk_size, overlap = 2000, 200
        step = chunk_size - overlap
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
        all_json = []
        for i, chunk in enumerate(chunks):
            if on_chunk_start:
                await on_chunk_start(i, len(chunks), len(chunk))
            try:
                extracted = await self._extract_chunk(chunk, model, timeout)
                result = text_to_summary(extracted, chunk_index=i)
                result_json = json.dumps(result, ensure_ascii=False)
                all_json.append(result_json)
                if on_chunk_done:
                    await on_chunk_done(i, len(chunks), result_json)
                logger.info(f"[GenieX] Chunk {i+1}/{len(chunks)} done")
            except Exception as e:
                logger.error(f"[GenieX] Chunk {i+1} error: {e}")
                if on_chunk_error:
                    await on_chunk_error(i, str(e))
        return len(chunks), all_json

    async def health(self):
        try:
            url = f"{settings.geniex_api_url.rstrip('/')}/models"
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    models = [m["id"] for m in resp.json().get("data", [])]
                    return {"online": True, "models": models, "url": settings.geniex_api_url, "runtime": "geniex"}
                return {"online": False, "url": settings.geniex_api_url, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"online": False, "url": settings.geniex_api_url, "error": str(e)}
