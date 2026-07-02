"""NexaAI provider."""
import json, logging
import httpx
from core.config import settings
from .base import TranscriptProvider, ChunkStartCB, ChunkDoneCB, ChunkErrorCB
from ..prompts import build_extraction_prompts, text_to_summary

logger = logging.getLogger(__name__)

class NexaProvider(TranscriptProvider):
    @property
    def name(self) -> str:
        return "nexa"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    async def summarize(self, text, model=None, language="hu", custom_prompt="",
                        on_chunk_start=None, on_chunk_done=None, on_chunk_error=None):
        model = model or settings.nexa_llm_model
        timeout = settings.nexa_timeout
        chunk_size, overlap = 2000, 200
        step = chunk_size - overlap
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
        all_json = []
        for i, chunk in enumerate(chunks):
            if on_chunk_start:
                await on_chunk_start(i, len(chunks), len(chunk))
            try:
                sys_p, usr_p = build_extraction_prompts(chunk, model_name=model, language=language)
                url = f"{settings.nexa_base_url.rstrip('/')}/chat/completions"
                msgs = []
                if sys_p:
                    msgs.append({"role": "system", "content": sys_p})
                msgs.append({"role": "user", "content": usr_p})
                async with httpx.AsyncClient(timeout=timeout) as c:
                    r = await c.post(url, json={"model": model, "messages": msgs, "temperature": 0.2, "max_tokens": 512})
                    r.raise_for_status()
                    raw = r.json()["choices"][0]["message"]["content"]
                result = text_to_summary(raw, chunk_index=i)
                rj = json.dumps(result, ensure_ascii=False)
                all_json.append(rj)
                if on_chunk_done:
                    await on_chunk_done(i, len(chunks), rj)
            except Exception as e:
                logger.error(f"[Nexa] Chunk {i+1} error: {e}")
                if on_chunk_error:
                    await on_chunk_error(i, str(e))
        return len(chunks), all_json
    
    async def health(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(f"{settings.nexa_base_url.rstrip('/')}/models")
                if r.status_code == 200:
                    models = [m["id"] for m in r.json().get("data",[])]
                    return {"online": True, "models": models, "url": settings.nexa_base_url}
        except Exception as e:
            return {"online": False, "error": str(e), "url": settings.nexa_base_url}
        return {"online": False, "url": settings.nexa_base_url}
