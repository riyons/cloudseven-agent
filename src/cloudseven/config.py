"""
Application configuration.

Uses pydantic-settings to load env vars with type validation.
Settings is a singleton — import `get_settings()` anywhere you need config.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings, loaded from .env with type validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ────────────────────────────────────────────────
    llm_provider: Literal["ollama", "anthropic", "openai"] = "ollama"

    ollama_model: str = "qwen2.5:14b"
    ollama_host: str = "http://localhost:11434"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"

    # ── Data ───────────────────────────────────────────────
    data_backend: Literal["json", "api", "postgres"] = "json"
    data_dir: Path = Field(default=Path("./data"))

    # ── Logging ────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_format: Literal["console", "json"] = "console"

    # ── App ────────────────────────────────────────────────
    app_env: Literal["development", "staging", "production"] = "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the singleton settings instance. Cached per-process."""
    return Settings()
