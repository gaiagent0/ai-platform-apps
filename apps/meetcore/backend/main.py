"""MeetCore — Meeting recording and AI summarization backend.

FastAPI application with domain-based architecture:
- /api/meetings — Meeting management
- /api/transcribe — Speech-to-text (Faster-Whisper / Parakeet)
- /api/tts — Text-to-speech (Piper)
- /api/chat — Meeting-aware Q&A (LiteLLM)
- /health — Health check
"""

from __future__ import annotations

import os
import sys

# Ensure the backend directory is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .shared.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup/shutdown."""
    # Startup
    print(f"MeetCore backend starting on port {settings.backend_port}")
    print(f"  GenieX: {settings.geniex_base_url} [{settings.geniex_model}]")
    print(f"  LiteLLM: {settings.litellm_base_url}")
    print(f"  Whisper: {settings.whisper_model_size} ({settings.whisper_language})")
    yield
    # Shutdown
    print("MeetCore backend shutting down")


app = FastAPI(
    title="MeetCore",
    description="Meeting recording and AI summarization backend",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow Open WebUI and local frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "meetcore",
        "version": "2.0.0",
    }


# Register routers
from .meetings.router import router as meetings_router
from .transcript.router import router as transcript_router
from .tts.router import router as tts_router
from .chat.router import router as chat_router

app.include_router(meetings_router)
app.include_router(transcript_router)
app.include_router(tts_router)
app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.backend_port,
        reload=True,
        log_level="info",
    )
