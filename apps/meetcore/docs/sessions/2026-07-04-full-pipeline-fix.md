# Session: 2026-07-04 — Full Pipeline Fix

## Summary

Teljes körű hibajavítás a meetcore backend-ben: a meeting processing pipeline
eddig nem mentette az adatokat az adatázisba, és a LiteLLM kapcsolat is
hibás volt.

## Talált és javított hibák

### 1. LiteLLM API Key (401 Unauthorized)
- **Probléma**: `MEETCORE_LITELLM_API_KEY=sk-local` nem egyezett a proxy master key-jel
- **Javítás**: `.env`-ben `sk-win-vivo2`-re állítva (gitignored)

### 2. LiteLLM Model: openrouter-default → qwen2.5:7b
- **Probléma**: `openrouter-default` cloud-based, felesleges local-first rendszerben
- **Javítás**: `qwen2.5:7b` (local Ollama, non-thinking mode, tiszta JSON output)
- **Miért nem qwen3**: Qwen3 thinking mode üres content-et ad vissza

### 3. Model konfigurálhatóság
- **Javítás**: `MEETCORE_LITELLM_MODEL` env var hozzáadva a config.py-hoz
- **litellm_client.py**: model paraméter `None` default, fallback `settings.litellm_model`-re

### 4. DB Write: transcript/summary nem íródik az adatázisba
- **Probléma**: `process_meeting` a `meetings` táblába próbálta menteni a transcript-et,
  de a `meetings` táblában nincs `transcript` oszlop
- **Javítás**: `create_transcript_chunk()` és `create_summary_process()` függvények
  hozzáadva a repository.py-hoz, INSERT a helyes táblákba

### 5. Status case sensitivity
- **Probléma**: `get_meeting_with_details` `status == "COMPLETED"`-et keres,
  de a mentés `"completed"` (kisbetűvel)
- **Javítás**: lekérdezés `"completed"`-re változtatva

### 6. Dockerfile: ghcr.io auth denied
- **Probléma**: `COPY --from=ghcr.io/astral-sh/uv:latest` auth hibával bukik
- **Javítás**: `curl -LsSf https://astral.sh/uv/install.sh` telepítésre cserélve

### 7. faster-whisper hiányzó dependency
- **Probléma**: `faster_whisper` importálva volt de nem szerepelt a pyproject.toml-ban
- **Javítás**: `faster-whisper>=1.1.0` hozzáadva

### 8. Docker DNS: host.docker.internal
- **Probléma**: A container nem tudta elérni a LiteLLM proxy-t a host-on
- **Javítás**: `extra_hosts: ["host.docker.internal:host-gateway"]` a docker-compose.yml-ben

## Eredmény

- ✅ 21/21 backend teszt átmegy
- ✅ E2E pipeline működik: upload → transcribe → summarize → completed
- ✅ /details endpoint visszaadja a transcript-et és summary-t
- ✅ Frontend build + Docker container fut
- ✅ 15+ commit eljutott az origin-re

## Beküldött commitok (session)

- `c52816b` docs: add README.md and ROADMAP.md
- `fd30001` fix: add extra_hosts for host.docker.internal DNS resolution
- `c81c2ac` fix: WAV conversion in save_recording + error handling improvements
- `6567aa7` fix: file_path→audio_path in transcribe call + add faster-whisper dep
- `307eea6` fix: add missing status field to get_meeting_with_details
- `c0e41c0` fix: replace ghcr.io COPY with curl install for uv in Dockerfile
- `791756e` fix: eliminate double get_result_dict() call, use summary_text for rendering
- `c72bc8e` feat: frontend /details integration, summary_text, API docs
- `53c266d` feat: make LiteLLM model configurable via settings
- `f5512e6` fix: LiteLLM auth + local model for summarization
