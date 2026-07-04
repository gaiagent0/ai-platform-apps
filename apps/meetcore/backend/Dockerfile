# MeetCore Backend — Python 3.12 slim
FROM python:3.12-slim

WORKDIR /app

# Install system deps: audio libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
# Install uv via curl (ghcr.io blocked by auth in Docker Hub)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && mv /root/.local/bin/uv /usr/local/bin/uv

# Copy all source code first (needed for non-editable install)
COPY . .

# Install Python dependencies (non-editable, no -e flag)
RUN uv pip install --system --no-cache .

# Install piper-tts via pip (not available in Debian repos)
RUN pip install --no-cache-dir piper-tts

# Create data directories
RUN mkdir -p /data/recordings /data/transcripts /data/audio

# Expose backend port
EXPOSE 5167

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:5167/health || exit 1

# Start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5167"]
