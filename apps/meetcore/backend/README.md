# MeetCore Backend API

FastAPI backend for meeting recording, transcription, and AI summarization.

## Endpoints

### Meetings

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/meetings/` | List all meetings |
| `POST` | `/api/meetings/` | Create a new meeting |
| `GET` | `/api/meetings/{id}` | Get meeting details (basic) |
| `GET` | `/api/meetings/{id}/details` | Get full meeting details (transcript, summary, action_items, topics) |
| `GET` | `/api/meetings/{id}/transcript` | Get only the transcript text |
| `DELETE` | `/api/meetings/{id}` | Delete a meeting |
| `DELETE` | `/api/meetings/{id}/force` | Delete with confirmation response |
| `POST` | `/api/meetings/{id}/upload` | Upload a recording (multipart/form-data) |
| `POST` | `/api/meetings/{id}/process` | Trigger processing (background task) |
| `POST` | `/api/meetings/cleanup-stale` | Reset stuck jobs (requires `MEETCORE_ADMIN_KEY` auth) |

### Processing Pipeline

When you call `POST /{id}/process`, the following happens asynchronously:

1. Status set to `processing`
2. Audio transcription via Faster-Whisper (`transcribing` -> `transcribed`)
3. LLM summarization via LiteLLM (`summarizing` -> `completed`)
4. Results saved: transcript, summary, action_items, topics

Status flow: `processing` -> `transcribing` -> `transcribed` -> `summarizing` -> `completed`

### Transcription

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/transcribe/` | Transcribe uploaded audio file |

### Text-to-Speech

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/tts/` | Generate speech from text |

### Chat

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chat/` | Ask a question about a meeting |

### Health

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MEETCORE_BACKEND_PORT` | `5167` | Backend port |
| `MEETCORE_DATABASE_URL` | `sqlite+aiosqlite:///./meeting_minutes.db` | Database URL |
| `MEETCORE_CORS_ORIGINS` | `["http://localhost:3118"]` | Allowed CORS origins |
| `MEETCORE_GENIEX_API_URL` | `http://localhost:8912/v1` | GenieX NPU endpoint |
| `MEETCORE_LITELLM_BASE_URL` | `http://host.docker.internal:4001` | LiteLLM gateway |
| `MEETCORE_WHISPER_LANGUAGE` | `hu` | Transcription language |
| `MEETCORE_ADMIN_KEY` | (empty) | Auth key for cleanup-stale |
| `MEETCORE_RECORDINGS_DIR` | `/data/recordings` | Audio file storage |

## Running

```bash
# Local development
pip install -r requirements.txt
uvicorn main:app --reload --port 5167

# Docker
docker compose build && docker compose up -d
```

## Testing

```bash
PYTHONPATH=. python -m pytest tests/ -v
```
