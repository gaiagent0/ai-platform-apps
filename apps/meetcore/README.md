# MeetCore

AI-powered meeting transcription, summarization, and Q&A platform.

## Architecture

- **Backend**: FastAPI (Python 3.12) — `/api/meetings`, `/api/transcribe`, `/api/tts`, `/api/chat`
- **Frontend**: Next.js — meeting list, detail page with transcript/summary
- **Storage**: SQLite (aiosqlite) — meets, transcripts, summaries
- **AI**: Faster-Whisper (STT), LiteLLM gateway (summarization), Piper TTS

## Processing Pipeline

```
POST /api/meetings/{id}/process
  → processing → transcribing → transcribed → summarizing → completed
```

1. **Upload**: MP3/WAV → ffmpeg converts to WAV (16kHz mono)
2. **Transcription**: Faster-Whisper (base model, CPU, int8)
3. **Summarization**: LiteLLM chat completion → summary + action items + topics

## Quick Start

```bash
# Local development
uvicorn backend.main:app --reload --port 5167

# Docker
docker compose up -d
```

## Testing

```bash
cd backend && PYTHONPATH=. python -m pytest tests/ -v
```

## Known Issues

- **LiteLLM 401 Unauthorized**: The summarization step requires a valid `MEETCORE_LITELLM_API_KEY` in `.env`. The default `sk-local` only works with an unauthenticated LiteLLM gateway.
- **SQLite is ephemeral**: Database resets on container rebuild. Consider mounting a volume for production.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/meetings/` | List all meetings |
| POST | `/api/meetings/` | Create meeting |
| GET | `/api/meetings/{id}` | Get meeting |
| GET | `/api/meetings/{id}/details` | Full details (transcript, summary) |
| POST | `/api/meetings/{id}/upload` | Upload recording |
| POST | `/api/meetings/{id}/process` | Trigger AI pipeline |
| GET | `/api/meetings/{id}/transcript` | Get transcript text |
| POST | `/api/transcribe/` | Standalone transcription |
| POST | `/api/tts/` | Text-to-speech |
| POST | `/api/chat/` | Chat about a meeting |
| GET | `/health` | Health check |
