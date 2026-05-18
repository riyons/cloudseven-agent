"""
Phase 2 chatbot: a stateful conversation wrapper with tool-calling support.

This is deliberately a class rather than a free function — when we add LangGraph
in Phase 3, we can swap the internals while keeping `Conversation.send()` as
the public interface. The scripts/chat.py CLI doesn't have to change at all.
"""
from __future__ import annotations

import json
from typing import Any

from cloudseven.agent.prompts import CLOUDSEVEN_ASSISTANT_PROMPT
from cloudseven.llm.base import LLMClient
from cloudseven.logging_config import get_logger
from cloudseven.tools.executor import ToolExecutor
from cloudseven.tools.schemas import ALL_TOOL_SCHEMAS

log = get_logger(__name__)


class Conversation:
    """Maintains conversation history, dispatches to the LLM, executes tools."""

    def __init__(
        self,
        llm: LLMClient,
        executor: ToolExecutor,
        system_prompt: str = CLOUDSEVEN_ASSISTANT_PROMPT,
        max_tool_iterations: int = 5,
    ) -> None:
        self._llm = llm
        self._executor = executor
        self._system_prompt = system_prompt
        self._max_iterations = max_tool_iterations
        self._messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
        ]

    def send(self, user_message: str) -> str:
        """Send a user message and return the assistant reply, executing
        any tool calls the LLM requests along the way."""
        self._messages.append({"role": "user", "content": user_message})
        log.info("user_message_sent", chars=len(user_message))

        for iteration in range(self._max_iterations):
            response = self._llm.chat_with_tools(self._messages, ALL_TOOL_SCHEMAS)

            # No tool calls — the LLM is done. Record the reply and return.
            if not response["tool_calls"]:
                reply = response["content"]
                self._messages.append({"role": "assistant", "content": reply})
                log.info(
                    "assistant_reply",
                    iteration=iteration,
                    chars=len(reply),
                    input_tokens=response.get("input_tokens"),
                    output_tokens=response.get("output_tokens"),
                )
                return reply

            # Tool calls present. Record the assistant's request, then execute.
            self._messages.append(self._assistant_tool_call_message(response))
            log.info(
                "tool_calls_requested",
                iteration=iteration,
                n_tool_calls=len(response["tool_calls"]),
                tools=[tc["name"] for tc in response["tool_calls"]],
            )

            for tool_call in response["tool_calls"]:
                result = self._executor.execute(
                    tool_call["name"], tool_call["arguments"]
                )
                self._messages.append(self._tool_result_message(tool_call, result))
                log.info(
                    "tool_executed",
                    iteration=iteration,
                    tool=tool_call["name"],
                    has_error="error" in result,
                )

        # Iteration cap exceeded — bail gracefully.
        log.warning("max_tool_iterations_exceeded", limit=self._max_iterations)
        fallback = (
            "I was unable to complete your request after several attempts. "
            "Could you try rephrasing your question, or break it into smaller parts?"
        )
        self._messages.append({"role": "assistant", "content": fallback})
        return fallback

    def reset(self) -> None:
        """Clear conversation history but keep the system prompt."""
        self._messages = [{"role": "system", "content": self._system_prompt}]
        log.info("conversation_reset")

    @property
    def message_count(self) -> int:
        """Number of messages excluding the system prompt."""
        return len(self._messages) - 1

    @staticmethod
    def _assistant_tool_call_message(response: dict[str, Any]) -> dict[str, Any]:
        """Translate our internal flat ToolCall shape into Ollama's nested wire
        format for the assistant message that requested the tool calls."""
        return {
            "role": "assistant",
            "content": response["content"],  # usually empty when calling tools
            "tool_calls": [
                {
                    "id": tc["id"],
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"],
                    },
                }
                for tc in response["tool_calls"]
            ],
        }

    @staticmethod
    def _tool_result_message(
        tool_call: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any]:
        """Wrap an executor result in Ollama's tool-role message shape.
        Note: content must be a JSON string, not a dict."""
        return {
            "role": "tool",
            "name": tool_call["name"],
            "content": json.dumps(result),
        }