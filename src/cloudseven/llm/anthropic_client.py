"""
Anthropic LLM client.

Stub for Phase 2 — left unimplemented to avoid a hard dependency on the
anthropic package in Phase 1. When you're ready, install with:
    pip install -e ".[phase2]"
and replace the body of `chat()`.
"""
from __future__ import annotations

from cloudseven.llm.base import ChatResponse, Message


class AnthropicClient:
    """LLMClient implementation backed by Anthropic. Phase 2+."""

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def chat(self, messages: list[Message]) -> ChatResponse:
        raise NotImplementedError("AnthropicClient will be implemented in Phase 2")
