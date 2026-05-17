"""
Ollama LLM client.

Talks to a local Ollama server (default localhost:11434).
Supports both plain chat (Phase 1) and tool-calling chat (Phase 2).
"""
from __future__ import annotations

import uuid
from typing import Any

import ollama

from cloudseven.domain.exceptions import LLMError
from cloudseven.llm.base import ChatResponse, Message, ToolCall
from cloudseven.logging_config import get_logger

log = get_logger(__name__)


class OllamaClient:
    """LLMClient implementation backed by Ollama."""

    def __init__(self, model: str, host: str) -> None:
        self._model = model
        self._client = ollama.Client(host=host)

    def chat(self, messages: list[Message]) -> ChatResponse:
        """Plain chat without tools. Returns text-only response."""
        log.debug(
            "llm_request", provider="ollama", model=self._model,
            n_messages=len(messages), tools=False,
        )
        response = self._invoke(messages, tools=None)
        return self._parse_response(response)

    def chat_with_tools(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
    ) -> ChatResponse:
        """Chat with tool schemas attached. Response may contain tool_calls."""
        log.debug(
            "llm_request", provider="ollama", model=self._model,
            n_messages=len(messages), tools=True, n_tools=len(tools),
        )
        response = self._invoke(messages, tools=tools)
        return self._parse_response(response)

    # ── Internals ────────────────────────────────────────────────────

    def _invoke(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        """Single point of contact with the ollama library. Translates errors."""
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": list(messages),
        }
        if tools is not None:
            kwargs["tools"] = tools

        try:
            return self._client.chat(**kwargs)
        except Exception as e:  # noqa: BLE001 — translated to our own type
            log.exception("llm_request_failed", provider="ollama", error=str(e))
            raise LLMError(f"Ollama call failed: {e}") from e

    def _parse_response(self, raw: dict[str, Any]) -> ChatResponse:
        """Normalize Ollama's response into our ChatResponse shape."""
        message = raw.get("message", {})
        content = message.get("content", "") or ""

        # Ollama returns tool_calls as a list of dicts shaped like:
        #   {"function": {"name": "...", "arguments": {...}}}
        # We normalize into our ToolCall TypedDict and synthesize an id
        # if Ollama didn't provide one (older versions sometimes omit it).
        raw_tool_calls = message.get("tool_calls") or []
        tool_calls: list[ToolCall] = []
        for raw_tc in raw_tool_calls:
            func = raw_tc.get("function", {})
            tool_calls.append(
                ToolCall(
                    id=raw_tc.get("id") or f"call_{uuid.uuid4().hex[:12]}",
                    name=func.get("name", ""),
                    arguments=func.get("arguments", {}) or {},
                )
            )

        input_tokens = raw.get("prompt_eval_count")
        output_tokens = raw.get("eval_count")

        log.debug(
            "llm_response", provider="ollama",
            input_tokens=input_tokens, output_tokens=output_tokens,
            response_chars=len(content), n_tool_calls=len(tool_calls),
        )

        return ChatResponse(
            content=content,
            tool_calls=tool_calls,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )