# Architectura

## A modularis AI Platform Apps rendszer

### Core elv: Pinokio-szeru modularitas

Minden alkalmazas **onallo modul**, amely:
- sajat docker-compose.yml vagy nativ indito script
- sajat app.json definicio (nev, port, fuggosegek, modellek)
- sajat .env konfiguracio
- a kozos modelleket szimlinken keresztul eri el

### SDK valtas: GenieAPIService → GenieX (2026)

**Fontos!** A Qualcomm attert a GenieX SDK-ra, amely:
- `pip install geniex`-szel telepul
- Tobb runtime: llama.cpp (GGUF) + qairt (NPU)
- OpenAI-kompatibilis API szerver
- Jobb dokumentacio: https://geniex.aihub.qualcomm.com/

### Foundry status

- **Windows nativen**: teljes NPU + GPU hozzaferes
- **WSL2-ben**: csak CPU (nincs NPU pass-through)

### Technologiai valasztasok

| Osszetevo | Valasztas | Alternativa |
|---|---|---|
| CLI framework | Typer (Python) | Click, oclif |
| UI | Rich | textual |
| Container | Docker Compose | nincs alternativa |
| AI SDK (NPU) | GenieX | LiteLLM (cloud) |
| Python PM | uv | pip, poetry |
| Node PM | pnpm | npm, yarn |
| ASR (batch) | Faster-Whisper | Whisper.cpp |
| ASR (NPU) | Parakeet TDT | N/A |
| TTS (gyors) | Piper | Kokoro |
| TTS (minosegi) | Kokoro | Coqui VITS |
| TTS (klonozas) | F5-TTS | GPT-SoVITS |
| Doc parser | MinerU / Docling | LlamaParse |
| Dubbing | VideoLingo / KrillinAI | custom pipeline |
| Lip-sync | LatentSync / LipDub | Wav2Lip |

### Rendszer integracio

Minden modul MCP protokollon keresztul kapcsolodik az Open WebUIhoz es a meglevo
infrastrukturahoz (LiteLLM, Langfuse, Qdrant, Mem0).
