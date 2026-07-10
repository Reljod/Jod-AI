from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "Jod-AI"
    debug: bool = False
    log_level: str = "INFO"

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_default_model: str = "openai/gpt-4o-mini"
    openrouter_max_tokens: int = 4096
    openrouter_temperature: float = 0.7
    openrouter_site_url: str = ""
    openrouter_site_name: str = "Jod-AI"

    # Database
    database_url: str = "postgresql+asyncpg://jod:jod_secret@localhost:5432/jod_ai"
    database_url_sync: str = "postgresql+psycopg2://jod:jod_secret@localhost:5432/jod_ai"

    # Context management
    max_context_tokens: int = 128_000
    context_compaction_threshold: float = 0.75
    summary_model: str = "openai/gpt-4o-mini"

    # File storage
    file_storage_path: str = "./data/files"
    max_file_size_mb: int = 50

    # Agent
    max_sub_agents: int = 5
    agent_recursion_limit: int = 100
    agent_timeout_seconds: int = 300


@lru_cache
def get_settings() -> Settings:
    return Settings()
