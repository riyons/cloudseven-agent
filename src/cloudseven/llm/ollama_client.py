"""
Ollama LLM client.

Talks to a local Ollama server (default localhost:11434).
No API key, no cost, no rate limit — but slower and weaker than cloud models.
"""
from __future__ import annotations

import ollama

from cloudseven.domain.exceptions import LLMError
from cloudseven.llm.base import ChatResponse, Message
from cloudseven.logging_config import get_logger

log = get_logger(__name__)


class OllamaClient:
    """LLMClient implementation backed by Ollama."""

    def __init__(self, model: str, host: str) -> None:
        self._model = model
        self._client = ollama.Client(host=host)

    def chat(self, messages: list[Message]) -> ChatResponse:
        log.debug("llm_request", provider="ollama", model=self._model, n_messages=len(messages))
        try:
            response = self._client.chat(model=self._model, messages=list(messages))
        except Exception as e:  # noqa: BLE001 — surface as our own error type
            log.exception("llm_request_failed", provider="ollama", error=str(e))
            raise LLMError(f"Ollama call failed: {e}") from e

        content = response["message"]["content"]
        # Ollama exposes eval counts; we map them to the same shape as cloud providers.
        input_tokens = response.get("prompt_eval_count")
        output_tokens = response.get("eval_count")

        log.debug(
            "llm_response",
            provider="ollama",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_chars=len(content),
        )
        return ChatResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
