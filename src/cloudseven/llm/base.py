"""
Abstract LLM client interface.

Keep this surface minimal. We'll extend it in Phase 2 to support tool calling,
but for Phase 1 a single `chat()` method is enough.
"""
from __future__ import annotations

from typing import Literal, Protocol, TypedDict


class Message(TypedDict):
    """Chat message format. Mirrors what every major LLM API uses."""

    role: Literal["system", "user", "assistant"]
    content: str


class ChatResponse(TypedDict):
    """Normalized response shape across providers."""

    content: str
    input_tokens: int | None
    output_tokens: int | None


class LLMClient(Protocol):
    """Interface every LLM provider implementation must satisfy."""

    def chat(self, messages: list[Message]) -> ChatResponse:
        """Send a chat request and return the assistant reply."""
        ...
