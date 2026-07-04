# MeetCore Backend — Python 3.12 slim
FROM python:3.12-slim

WORKDIR /app

# Install system deps: Piper TTS + audio libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libsndfile1 \
    ffmpeg \
    piper-tts \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY .env.example .env

# Install dependencies
RUN uv pip install --system -e .

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /data/recordings /data/transcripts /data/audio

# Expose backend and MCP ports
EXPOSE 5167 8007

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5167/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5167"]
