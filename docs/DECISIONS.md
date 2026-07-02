# Technologiai Dontesek (ADRs)

## ADR-001: SDK valasztas
- **Dontes**: GenieX SDK a GenieAPIService helyett
- **Indoklas**: A GenieX a hivatalos publikus SDK, tobb runtime, jobb dokumentacio
- **Kovetkezmeny**: A MeetCore-t at kell irni GenieX-re

## ADR-002: CLI framework
- **Dontes**: Python Typer + Rich
- **Alternativak**: Click, oclif (Node.js)
- **Indoklas**: Typer gyors fejlesztes, tipus-hint alapjan CLI argumentumok

## ADR-003: Alkalmazas formatum
- **Dontes**: Minden modul sajat docker-compose.yml + app.json
- **Alternativak**: NixOS, Pinokio script, natív telepito
- **Indoklas**: Docker Compose a legjobb egyensuly a megbizhatosag es konnyu hasznalat kozott

## ADR-004: ASR engine
- **Dontes**: Faster-Whisper large-v3 (alap), Parakeet TDT (NPU alternativa)
- **Indoklas**: Whisper jobb magyar nyelvre, Parakeet gyorsabb de kevesebb nyelv

## ADR-005: TTS engine
- **Dontes**: Piper (gyors, CPU) + Kokoro (minosegi) + F5-TTS (klonozas)
- **Licencek**: Piper MIT, Kokoro Apache 2.0, F5-TTS CC-BY-NC

## ADR-006: Dokumentum parser
- **Dontes**: MinerU (altalanos) + Docling (IBM, mar hasznalatban)
- **Licenc**: Apache 2.0 / MIT

## ADR-007: Dubbing pipeline
- **Dontes**: VideoLingo vagy KrillinAI (valaszthato)
- **Lip-sync**: LatentSync vagy LipDub (diffusion-based)
