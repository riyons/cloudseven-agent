"""LLM client factory — picks implementation based on config."""
from __future__ import annotations

from cloudseven.config import get_settings
from cloudseven.llm.base import LLMClient
from cloudseven.llm.ollama_client import OllamaClient


def get_llm_client() -> LLMClient:
    settings = get_settings()

    if settings.llm_provider == "ollama":
        return OllamaClient(model=settings.ollama_model, host=settings.ollama_host)

    if settings.llm_provider == "anthropic":
        # Lazy import so phase 1 doesn't require the package
        from cloudseven.llm.anthropic_client import AnthropicClient

        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not set in .env")
        return AnthropicClient(
            api_key=settings.anthropic_api_key, model=settings.anthropic_model
        )

    raise NotImplementedError(f"llm_provider={settings.llm_provider} not supported yet")
