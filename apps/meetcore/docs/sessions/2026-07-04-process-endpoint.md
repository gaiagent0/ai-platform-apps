# Session: 2026-07-04 — Process Endpoint Implementation

## Summary

Implemented the full meeting processing pipeline (transcription + LLM summarization) and fixed a fundamental Next.js proxy bug.

## Commits

| Hash | Description |
|---|---|
| `0973a8a` | Proxy fix: NEXT_PUBLIC_API_URL direct CORS, removed broken Next.js rewrite |
| `6be0ec7` | Process endpoint: Faster-Whisper transcription + LiteLLM summarization |
| `52e52c8` | Refactor: BackgroundTasks, narrowed exceptions, model param fix |
| `fb5a0b4` | Progress tracking + cleanup-stale endpoint + 3 integration tests |
| `721d8a3` | Cleanup-stale HTTPBearer auth + test cleanup fixture |

## Architecture

```
Browser -> Frontend (localhost:3118) -> Backend (localhost:5167)
                                        |
                                        |-- POST /api/meetings/ -> create
                                        |-- POST /api/meetings/{id}/upload -> save WAV
                                        |-- POST /api/meetings/{id}/process -> BackgroundTask
                                        |     |-- TranscriptService.transcribe() [Faster-Whisper]
                                        |     +-- chat_completion() [LiteLLM]
                                        |-- POST /api/meetings/cleanup-stale -> reset stuck jobs
                                        +-- DELETE /api/meetings/{id} -> delete
```

## Key Decisions

1. **Direct CORS over Next.js proxy**: Next.js `:path*` rewrite strips trailing slashes, causing redirect loops. Client-side JS calls backend directly via `NEXT_PUBLIC_API_URL`.
2. **BackgroundTasks**: Process endpoint returns immediately with `processing` status. Transcription + summarization runs in background.
3. **Progress tracking**: Status flow: `processing` -> `transcribing` -> `summarizing` -> `completed`/`error`.
4. **HTTPBearer auth**: `cleanup-stale` requires `MEETCORE_ADMIN_KEY` env var. Open access when unset (dev-friendly).

## Verified

- 19/19 backend tests pass (including mocked pipeline test)
- Frontend builds cleanly
- Full CRUD flow (create -> upload -> process -> get -> list -> delete)
- CORS headers correct for browser direct calls
- Auth on cleanup-stale endpoint works
- Mocked pipeline test verifies end-to-end flow
