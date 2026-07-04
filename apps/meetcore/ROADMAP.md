# MeetCore Roadmap

## ✅ Completed

- [x] Meeting CRUD (create, list, get, delete)
- [x] Audio upload (MP3/WAV with auto-conversion)
- [x] Background processing pipeline (processing→transcribing→summarizing→completed)
- [x] Faster-Whisper transcription (base model, CPU)
- [x] Summary generation via LiteLLM
- [x] /details endpoint (transcript, summary, action_items, topics)
- [x] Frontend: meeting list + detail page with summary_text rendering
- [x] Docker deployment (backend + frontend)
- [x] 21 backend tests passing
- [x] Docker DNS fix (host.docker.internal for LiteLLM access)
- [x] RIFF header check + ffmpeg conversion for non-WAV uploads

## 🔧 In Progress / Known Issues

- [ ] **LiteLLM auth**: 401 Unauthorized on summarization — need valid API key in MEETCORE_LITELLM_API_KEY
- [ ] **SQLite persistence**: Database resets on container rebuild — mount volume for production
- [ ] **Empty transcript on /details**: Transcription runs but /details returns empty — investigate DB write path

## 📋 Next Steps

### Phase 1: Production Hardening
- [ ] Add persistent volume for SQLite database
- [ ] Configure LiteLLM API key properly
- [ ] Add error logging/monitoring for background tasks
- [ ] Add meeting duration calculation from audio metadata

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
