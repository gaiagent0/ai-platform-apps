# AI Platform Apps

## Attekintes

Modularis AI alkalmazas rendszer Pinokio-szeru architekturaval.
Minden alkalmazas onalloan telepitheto a sajat fuggosegeivel.

## Kapcsolodo rendszerek

- **ai-platform-os** (../ai-platform-os/): Meglevo infrastruktura
  - LiteLLM :4001 - AI gateway
  - Qdrant :6333 - Vektor adatbazis
  - Langfuse :3000 - Observability
  - Mem0 :8008 - Agent memoria
  - Open WebUI - Chat UI
  - n8n :5678 - Workflow

- **meetcore** (../meetcore/): Meeting asszisztens (migralando)
  - GenieAPIService -> GenieX SDK atiras
  - MCP wrapper az Open WebUI-hoz

## CLI parancsok

ai-apps install <name>  -- Telepites git repobol
ai-apps start <name>    -- Inditas
ai-apps stop <name>     -- Leallitas
ai-apps status          -- Allapot
ai-apps list            -- Modulok listaja

## SDK valtas

A GenieAPIService elavult. A Qualcomm hivatalos SDK-ja a GenieX:
- pip install geniex
- Tobb runtime: llama.cpp (GGUF) + qairt (NPU)
- OpenAI-kompatibilis API
- https://geniex.aihub.qualcomm.com/
