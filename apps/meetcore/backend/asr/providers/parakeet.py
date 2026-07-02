"""Parakeet TDT ASR via NexaAI."""
import logging
import httpx
from core.config import settings

logger = logging.getLogger(__name__)

class ParakeetASRProvider:
    @property
    def name(self):
        return "parakeet"

    async def transcribe(self, audio_bytes: bytes, language: str = "hu", content_type: str = "audio/webm") -> str:
        url = f"{settings.nexa_base_url.rstrip('/')}/audio/transcriptions"
        async with httpx.AsyncClient(timeout=120.0) as c:
            resp = await c.post(url,
                files={"file": ("audio.wav", audio_bytes, content_type)},
                data={"model": settings.nexa_asr_model, "language": language})
            resp.raise_for_status()
            result = resp.json()
        return (result.get("text") or result.get("transcript") or "").strip()

    async def health(self):
        try:
            async with httpx.AsyncClient(timeout=3.0) as c:
                r = await c.get(f"{settings.nexa_base_url.rstrip('/')}/models")
                return {"online": r.status_code < 500, "url": settings.nexa_base_url}
        except Exception as e:
            return {"online": False, "error": str(e)}
