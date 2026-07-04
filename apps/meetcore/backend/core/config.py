"""
config.py — MeetCore v3
Pydantic Settings based configuration.

All environment variables in one place with validation.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ── App ──
    app_name: str = "MeetCore"
    app_version: str = "3.0.0"
    debug: bool = False
    backend_port: int = 5167
    cors_origins: list[str] = ["http://localhost:3118", "http://localhost:3000"]
    
    # ── Database ──
    database_url: str = "sqlite+aiosqlite:///./meeting_minutes.db"
    recordings_dir: str = "/data/recordings"
    
    # ── GenieX SDK (Qualcomm NPU) ──
    geniex_api_url: str = "http://localhost:8912/v1"
    geniex_api_key: str = "local"
    geniex_model: str = "llama3.1-8b-qat"
    geniex_timeout: float = 120.0
    
    # ── Ollama ──
    ollama_host: str = "http://localhost:11434"
    ollama_timeout: float = 300.0
    ollama_model: Optional[str] = None
    
    # ── NexaAI ──
    nexa_base_url: str = "http://127.0.0.1:18181/v1"
    nexa_timeout: float = 120.0
    nexa_llm_model: str = "NexaAI/Qwen3-8B-NPU"
    nexa_asr_model: str = "NexaAI/parakeet-tdt-0.6b-v3-npu"
    
    # ── OmniNeural ──
    omnineural_url: str = "http://127.0.0.1:18183/v1"
    omnineural_model: str = "NexaAI/OmniNeural-4B"
    
    # ── LiteLLM Gateway ──
    litellm_base_url: str = "http://host.docker.internal:4001"
    litellm_api_key: str = "sk-local"
    litellm_timeout: float = 120.0
    
    # ── ASR ──
    whisper_language: str = "hu"
    whisper_model_path: Optional[str] = None
    whisper_backend: str = "cpp"
    
    # ── TTS ──
    piper_model_path: Optional[str] = None
    piper_sample_rate: int = 22050
    piper_speed: float = 1.0
    tts_server_url: str = "http://localhost:7860"
    tts_timeout: float = 30.0
    f5_max_chars: int = 150
    f5_timeout: float = 300.0
    
    # ── MCP ──
    mcp_port: int = 8012
    
    model_config = {"env_prefix": "MEETCORE_"}


settings = Settings()
