"""Centralized configuration using pydantic-settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Backend
    backend_port: int = 5167

    # GenieX SDK (OpenAI-compatible NPU inference)
    geniex_base_url: str = "http://host.docker.internal:8912/v1"
    geniex_model: str = "llama3.1-8b-qat"
    geniex_api_key: str = "not-needed"

    # LiteLLM Gateway (cloud LLMs)
    litellm_base_url: str = "http://host.docker.internal:4001"
    litellm_api_key: str = ""

    # ASR (Speech-to-Text)
    whisper_language: str = "hu"
    whisper_model_size: str = "base"
    whisper_device: str = "auto"
    whisper_compute_type: str = "auto"

    # Parakeet ASR (NPU accelerated)
    parakeet_base_url: str = "http://host.docker.internal:18181"
    parakeet_model: str = "parakeet-tdt-0.6b-v3-npu"

    # TTS (Text-to-Speech)
    piper_voice: str = "hu_HU-dfpros-medium"
    piper_executable: str = "piper"

    # Langfuse Tracing
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "http://10.10.40.36:3000"

    # MCP Server
    mcp_port: int = 8007

    # Storage
    recordings_dir: str = "/data/recordings"
    transcripts_dir: str = "/data/transcripts"
    audio_dir: str = "/data/audio"


settings = Settings()
