"""MeetCore — Meeting recording and AI summarization backend (v3).

Integrates all domain modules:
- /meetings — Meeting CRUD (SQLAlchemy DB)
- /asr — Speech-to-text (Parakeet + WhisperCPP)
- /transcribe — Speech-to-text (Faster-Whisper via service)
- /tts — Text-to-speech (Piper)
- /chat — Meeting-aware Q&A (LiteLLM)
- /health — Health check
- MCP server on configurable port
"""

from __future__ import annotations

import os
import sys

# Ensure core module is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.db import init_db
from core.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup/shutdown."""
    setup_logging(debug=settings.debug)
    await init_db()
    print(f"MeetCore v{settings.app_version} starting on port {settings.backend_port}")
    print(f"  GenieX: {settings.geniex_api_url} [{settings.geniex_model}]")
    print(f"  LiteLLM: {settings.litellm_base_url}")
    print(f"  ASR: {settings.whisper_language} ({settings.whisper_backend})")
    print(f"  MCP port: {settings.mcp_port}")
    yield
    print("MeetCore shutting down")


app = FastAPI(
    title=settings.app_name,
    description="Meeting recording and AI summarization backend",
    version=settings.app_version,
    lifespan=lifespan,
    redirect_slashes=False,  # Prevent 307 redirects through Next.js proxy
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["http://localhost:3118", "http://localhost:5167", "http://127.0.0.1:3118"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# Register routers — new domain-based API
from meetings.router import router as meetings_router
from transcript.router import router as transcript_router
from tts.router import router as tts_router
from chat.router import router as chat_router

app.include_router(meetings_router)
app.include_router(transcript_router)
app.include_router(tts_router)
app.include_router(chat_router)

# Register routers — pre-existing modules
from asr.router import router as asr_router

app.include_router(asr_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True,
        log_level="info",
    )
