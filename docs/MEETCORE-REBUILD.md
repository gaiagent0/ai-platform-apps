# MeetCore Rebuild Plan

## Cel: GenieAPIService -> GenieX SDK + modern FastAPI + MCP

A jelenlegi MeetCore kodbazis elavult technologiakat hasznal.
A kovetkezo valtoztatasokat kell elvegezni:

## 1. SDK valtas: GenieAPIService -> GenieX

**Jelenleg:**
```python
# meetcore/backend/app/transcript_processor.py
GENIE_BASE_URL = "http://127.0.0.1:8912/v1"
# sajat http hivasok a GenieAPIService-hez
```

**Uj megoldas:**
```python
# pip install geniex
import geniex

# OpenAI-kompatibilis API (a GenieX beepitett szervere)
# A GenieX futtatasa:
#   geniex serve --model llama3.1-8b-qat --port 8912
#
# A meetcore ugy hivja, mint barmely OpenAI API-t:
import openai
client = openai.OpenAI(base_url="http://localhost:8912/v1", api_key="local")
response = client.chat.completions.create(
    model="llama3.1-8b-qat",
    messages=[...]
)
```

**Elonyok:**
- `pip install geniex` - egyszeru telepites
- Tobb runtime: llama.cpp (GGUF) + qairt (NPU)
- OpenAI-kompatibilis API - nincs sajat HTTP wrapper
- Jobb dokumentacio: https://geniex.aihub.qualcomm.com/

## 2. FastAPI modern struktura

**Jelenleg:** layer-alapu (minden egy /app/ mappaban)

**Uj struktura (domain-alapu):**
```
backend/
  main.py              # Csak routerek betoltese
  core/
    config.py          # Korzeti valtozok
    db.py              # SQLite / adatbazis
    logging.py         # Langfuse integration
  meetings/            # Meeting domain
    router.py          # API vegpontok
    service.py         # Uzleti logika
    schemas.py         # Pydantic modellek
    repository.py      # Adatbazis muveletek
  transcript/          # Atiras domain
    router.py
    service.py
    provider_geniex.py # GenieX SDK wrapper
    provider_ollama.py
    provider_cloud.py  # LiteLLM gateway
  tts/                 # TTS domain
    router.py
    service.py
    provider_piper.py
    provider_kokoro.py
  chat/                # Chat domain
    router.py
    service.py
  shared/
    mcp_server.py      # MCP wrapper
```

## 3. MCP Wrapper

Egy MCP szerver, amely a meetcore endpoint-jait MCP tool-kent expose-olja:

```python
# backend/shared/mcp_server.py
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meetcore")

@mcp.tool()
def record_meeting(duration_minutes: int) -> str:
    """Start meeting recording"""
    ...

@mcp.tool()
def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file to text"""
    ...

@mcp.tool()
def summarize_meeting(meeting_id: str, provider: str = "ollama") -> dict:
    """Generate AI summary for a meeting"""
    ...

@mcp.tool()
def get_meeting_context(meeting_id: str) -> str:
    """Get meeting context for RAG"""
    ...
```

**Open WebUI integráció:**
1. MCP tool-kent latszik a modell szamara
2. LiteLLM routolja a hivasokat
3. Langfuse trace-el mindent

## 4. LiteLLM Gateway

Az osszes cloud provider hivas (Claude, Groq, OpenAI, OpenRouter)
a LiteLLM gateway-en keresztul megy, nem direktben:

```python
# Jelenleg: direkt API hivas
response = httpx.post("https://api.openai.com/v1/chat/completions", ...)

# Uj: LiteLLM gateway
response = httpx.post(
    "http://host.docker.internal:4001/chat/completions",
    json={"model": "gpt-4o-mini", "messages": [...]}
)
# Elony: Langfuse trace, load balancing, failover
```

## 5. Modern tooling

| Jelenleg | Uj | Elony |
|---|---|---|
| pip | **uv** | 10-100x gyorsabb |
| setup.py | **pyproject.toml** | Standard |
| requirements.txt | **uv.lock** | Reprodukalhato |
| npm | **pnpm** (mar hasznalatban) | - |

## 6. Front-end modernizalasa

| Jelenleg | Uj |
|---|---|
| Next.js 15 | Next.js 15 (mar jo) |
| React 19 | React 19 Server Components |
| Richer UI | Shadcn/ui komponensek |

## Implementacios terv

1. GenieX SDK telepites es teszteles (pip install geniex)
2. transcripts_processor.py atirasa (GenieAPIService -> GenieX)
3. FastAPI struktura atalakitasa (domain-alapu)
4. MCP wrapper hozzaadasa
5. LiteLLM gateway beepitese
6. Teszteles (74 teszt van, ezeket is at kell irni)
7. Docker compose frissitese
