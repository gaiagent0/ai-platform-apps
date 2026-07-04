# MeetCore Roadmap

## ✅ Completed

- [x] Meeting CRUD (create, list, get, delete)
- [x] Audio upload (MP3/WAV with auto-conversion via ffmpeg)
- [x] Background processing pipeline (processing→transcribing→summarizing→completed)
- [x] Faster-Whisper transcription (base model, CPU, int8)
- [x] Summary generation via LiteLLM (qwen2.5:7b local)
- [x] /details endpoint (transcript, summary, action_items, topics)
- [x] Frontend: meeting list + detail page with summary_text rendering
- [x] Docker deployment (backend + frontend)
- [x] 21 backend tests passing
- [x] Docker DNS fix (host.docker.internal for LiteLLM access)
- [x] DB write fix: transcript → transcript_chunks, summary → summary_processes
- [x] LiteLLM auth fix (sk-win-vivo2 master key)
- [x] Model configurable via MEETCORE_LITELLM_MODEL env var
- [x] WAV conversion for non-WAV uploads (RIFF header check + ffmpeg)

## 🔧 Known Issues

- [ ] SQLite is ephemeral — database resets on container rebuild
- [ ] Segments array returns 0 (transcript_segments not populated separately)
- [ ] Summary JSON contains nested markdown code block (LLM wrapping)

## 📋 Next Steps

### Phase 1: Production Hardening
- [ ] Add persistent volume for SQLite database
- [ ] Fix summary JSON parsing (strip markdown code blocks)
- [ ] Add meeting duration calculation from audio metadata
- [ ] Add proper error logging for background tasks

### Phase 2: Features
- [ ] Chat endpoint: Q&A about meeting content using RAG
- [ ] Multi-language transcription support
- [ ] Speaker diarization (who said what)
- [ ] Export meeting notes (PDF/Markdown)
- [ ] Meeting search across all meetings

### Phase 3: Integration
- [ ] n8n workflow integration for automated meeting processing
- [ ] Langfuse observability for AI pipeline
- [ ] Webhook notifications when processing completes
- [ ] MCP server for Claude Desktop integration
