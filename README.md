# AI Platform Apps

> **Modularis, onalloan telepitheto AI alkalmazas rendszer**  
> Snapdragon X Elite NPU + GenieX SDK | Windows ARM64 + WSL2

---

## Atltekintes

Az `ai-platform-apps` egy **Pinokio-szeru modularrendszer**, ahol minden AI alkalmazas
**onalloan telepitheto** a sajat fuggosegeivel, konfiguraciojaival es modelljeivel.

## Kapcsolodo Repok

| Repo | Leiras |
|---|---|
| [ai-platform-os](https://github.com/gaiagent0/ai-platform-os) | Meglevo infra: Qdrant, LiteLLM, Langfuse, MCP szerverek |
| [meetcore](https://github.com/gaiagent0/meetcore) | Meeting hangrogzites + AI osszefoglalo |

## Modularis architektura

```
ai-platform-apps/
├── app-manager/        ← CLI (Typer + Rich)
├── apps/               ← Alkalmazas modulok
│   ├── meetcore/       ← Meeting asszisztens
│   ├── doc-reader/     ← Dokumentum → Beszed
│   ├── stt-engine/     ← Speech-to-Text
│   ├── dubbing-studio/ ← Film szinkronizalas
│   └── voice-assistant/← Hang asszisztens
├── docs/               ← Dokumentacio
├── shared/             ← Kozos modellek
└── scripts/            ← Telepito/karbantarto scriptek
```

## Hasznalat

```bash
# CLI telepites
cd app-manager && pip install -e .

# Modulok kezelese
ai-apps install meetcore
ai-apps start meetcore
ai-apps status
ai-apps list
```
