# Modulok reszletes leirasa

## 1. MeetCore (meeting assistant)

**Status**: Atiras alatt (GenieAPIService → GenieX)
**Port**: 3118 (frontend) + 5167 (backend)

**Funkciok**:
- Lokalis meeting hangrogzites
- Parakeet / Faster-Whisper ASR (magyar nyelv)
- 8 AI provider osszefoglalo
- Piper TTS felolvasas
- F5-TTS hangklonozas
- Meeting chat RAG-gal

**Fuggo repok**: gaiagent0/meetcore

## 2. DocReader (document to speech)

**Status**: Tervezes
**Port**: 5200

**Pipeline**:
Bemenet (PDF/DOCX/EPUB/HTML/MD)
  → MinerU / Docling (szoveg kinyeres)
  → Intelligent chunking
  → Kokoro / Piper TTS (magyar beszed)
  → FFmpeg (audio osszefuzes)
  → Kimenet (MP3 audiobook / WAV)

## 3. STT Engine (speech to text)

**Status**: Tervezes
**Port**: 5100 (API) + WebSocket

**Funkciok**:
- Hangfajl atiras (Faster-Whisper)
- Elo streaming ASR (WebSocket)
- Speaker diarization (pyannote-audio)
- Felirat generalas (SRT/VTT)
- YouTube video letoltes + atiras

## 4. Dubbing Studio (film szinkron)

**Status**: Tervezes
**Port**: 5300

**Pipeline**:
Bemenet (MP4/URL)
  → yt-dlp + FFmpeg
  → Demucs (hang szetvalasztas)
  → Whisper + WhisperX (atiras + diarization)
  → LiteLLM (forditas)
  → GPT-SoVITS / CosyVoice2 (hangklonozas)
  → LatentSync / LipDub (lip-sync)
  → FFmpeg (vegso video)
  → Kimenet (MP4 + SRT)

## 5. Voice Assistant (hang asszisztens)

**Status**: Tervezes
**Port**: 5400

**Pipeline**:
openWakeWord (ebresztes)
  → Silero VAD (hang detektalas)
  → Faster-Whisper (STT)
  → LiteLLM (LLM valasz)
  → Piper / Kokoro (TTS)
  → Kimenet (hang valasz)
