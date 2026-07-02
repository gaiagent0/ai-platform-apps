"""
GenieX Provider — Qualcomm NPU via GenieX SDK.

Two modes:
  1. OpenAI-compatible API server: geniex serve --model X --port 8912
  2. Python SDK: from geniex import AutoModelForCausalLM

Both modes are supported. Server mode is the default for simplicity.
"""

import json
import logging
from typing import Optional

import httpx

from core.config import settings
from .base import TranscriptProvider, ChunkStartCB, ChunkDoneCB, ChunkErrorCB
from ..prompts import build_extraction_prompts, text_to_summary, get_model_family

logger = logging.getLogger(__name__)


class GenieXProvider(TranscriptProvider):
    """
    Qualcomm NPU provider via GenieX SDK.
    Uses GenieX's OpenAI-compatible API server by default.
    """
    
    @property
    def name(self) -> str:
        return "geniex"
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    async def _extract_chunk(
        self,
        chunk: str,
        model: str,
        timeout: float,
        no_think: bool = False,
    ) -> str:
        """Process a single chunk via GenieX OpenAI-compatible API."""
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
            resp = await client.post(
                url,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": num_predict,
                },
            )
            resp.raise_for_status()
        
        raw = resp.json()["choices"][0]["message"]["content"]
        return raw
    
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
        """Summarize transcript via GenieX NPU."""
        model = model or settings.geniex_model
        timeout = settings.geniex_timeout
        
        # Chunk for NPU (smaller chunks → faster per-chunk)
        chunk_size = 2000
        overlap = 200
        step = chunk_size - overlap
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), step)]
        
        all_json: list[str] = []
        
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
    
    async def health(self) -> dict:
        """Check if GenieX API server is reachable."""
        try:
            url = f"{settings.geniex_api_url.rstrip('/')}/models"
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m["id"] for m in data.get("data", [])]
                    return {
                        "online": True,
                        "models": models,
                        "url": settings.geniex_api_url,
                        "runtime": "geniex",
                    }
                return {"online": False, "url": settings.geniex_api_url, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"online": False, "url": settings.geniex_api_url, "error": str(e)}


# ── Alternative: GenieX Python SDK mode ──
# This is a placeholder for native GenieX SDK usage
# Usage: from geniex import AutoModelForCausalLM
# Only available on Snapdragon X Elite with GenieX installed

class GenieXPythonSDKProvider(TranscriptProvider):
    """
    Alternative GenieX provider using the Python SDK directly.
    Requires: pip install geniex
    Only available on ARM64 Windows with Qualcomm NPU.
    """
    
    @property
    def name(self) -> str:
        return "geniex-sdk"
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
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
        try:
            from geniex import AutoModelForCausalLM
        except ImportError:
            logger.error("[GenieX-SDK] geniex not installed. Use 'geniex' provider with server mode.")
            raise RuntimeError(
                "GenieX Python SDK not installed. "
                "Run: pip install geniex
"
                "Or use 'geniex' provider with server mode (geniex serve --port 8912)"
            )
        
        model_name = model or settings.geniex_model
        geniex_model = AutoModelForCausalLM.from_pretrained(model_name)
        
        chunks = [text[i:i + 2000] for i in range(0, len(text), 1800)]
        all_json: list[str] = []
        
        for i, chunk in enumerate(chunks):
            if on_chunk_start:
                await on_chunk_start(i, len(chunks), len(chunk))
            
            try:
                prompt = f"Summarize this meeting transcript in Hungarian: {chunk}"
                result_text = ""
                for token in geniex_model.generate(prompt, max_new_tokens=512, stream=True):
                    result_text += token
                
                result = text_to_summary(result_text, chunk_index=i)
                result_json = json.dumps(result, ensure_ascii=False)
                all_json.append(result_json)
                
                if on_chunk_done:
                    await on_chunk_done(i, len(chunks), result_json)
            except Exception as e:
                logger.error(f"[GenieX-SDK] Chunk {i+1} error: {e}")
                if on_chunk_error:
                    await on_chunk_error(i, str(e))
        
        geniex_model.close()
        return len(chunks), all_json
    
    async def health(self) -> dict:
        try:
            from geniex import AutoModelForCausalLM
            return {"online": True, "sdk_available": True, "note": "Python SDK mode"}
        except ImportError:
            return {"online": False, "sdk_available": False, "note": "pip install geniex"}
