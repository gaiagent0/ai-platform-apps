# MeetCore

AI-powered meeting transcription, summarization, and Q&A platform.

## Architecture

- **Backend**: FastAPI (Python 3.12) — `/api/meetings`, `/api/transcribe`, `/api/tts`, `/api/chat`
- **Frontend**: Next.js — meeting list, detail page with transcript/summary
- **Storage**: SQLite (aiosqlite) — meetings, transcript_chunks, summary_processes
- **AI**: Faster-Whisper (STT), LiteLLM gateway (summarization via qwen2.5:7b), Piper TTS

## Processing Pipeline

```
POST /api/meetings/{id}/process
  → processing → transcribing → transcribed → summarizing → completed
```

1. **Upload**: MP3/WAV → ffmpeg auto-converts to WAV (16kHz mono) if not already RIFF
2. **Transcription**: Faster-Whisper (base model, CPU, int8)
3. **Summarization**: LiteLLM chat completion → summary + action items + topics
4. **Storage**: Transcript → transcript_chunks table, Summary → summary_processes table

## Quick Start

```bash
# Local development
uvicorn backend.main:app --reload --port 5167

# Docker
docker compose up -d
```

## Configuration

Environment variables (via `.env` or docker-compose):

| Variable | Default | Description |
|----------|---------|-------------|
| `MEETCORE_LITELLM_BASE_URL` | `http://host.docker.internal:4001` | LiteLLM gateway URL |
| `MEETCORE_LITELLM_API_KEY` | `sk-win-vivo2` | LiteLLM master key |
| `MEETCORE_LITELLM_MODEL` | `qwen2.5:7b` | Default model for summarization |
| `MEETCORE_WHISPER_LANGUAGE` | `hu` | Default transcription language |
| `MEETCORE_DATABASE_URL` | `sqlite+aiosqlite:///./meeting_minutes.db` | Database URL |

## Testing

```bash
cd backend && PYTHONPATH=. python -m pytest tests/ -v
```

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
