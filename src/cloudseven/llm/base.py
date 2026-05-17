"""
Abstract LLM client interface.

Extended in Phase 2 to support tool calling. The interface now has two
methods:
  - chat(messages)                  - plain text completion (Phase 1)
  - chat_with_tools(messages, tools) - tool-aware completion (Phase 2+)

ChatResponse is normalized across providers: every response has both a
content string and a tool_calls list. One will be meaningful; the other
will be empty. The agent loop branches on whether tool_calls is non-empty.
"""
from __future__ import annotations

from typing import Any, Literal, Protocol, TypedDict


class Message(TypedDict):
    """A single message in the conversation.

    Roles:
      - 'system'    : the system prompt (sent once at the start of history)
      - 'user'      : a message from the human user
      - 'assistant' : a message from the LLM. May contain text OR tool_calls.
      - 'tool'      : the result of executing a tool call. Paired to the
                      assistant message that requested it via tool_call_id.
    """

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    # Optional fields used only for specific roles:
    # - tool_calls: present on assistant messages that request tool execution
    # - tool_call_id / name: present on tool result messages


class ToolCall(TypedDict):
    """A single tool invocation requested by the LLM."""

    id: str
    """Unique identifier so tool results can be paired back to the request.

    Ollama generates these; we just propagate them. When we send back the
    tool's result, the corresponding tool message references this ID.
    """

    name: str
    """The name of the tool to call. Matches a key in the executor registry."""

    arguments: dict[str, Any]
    """JSON arguments for the tool, already parsed from the LLM's output."""


class ChatResponse(TypedDict):
    """Normalized response shape across LLM providers.

    Either `content` is non-empty (final text reply) OR `tool_calls` is
    non-empty (LLM wants to call tools). Never both meaningful at once;
    occasionally both empty if the model produced nothing useful.
    """

    content: str
    tool_calls: list[ToolCall]
    input_tokens: int | None
    output_tokens: int | None


class LLMClient(Protocol):
    """Interface every LLM provider implementation must satisfy."""

    def chat(self, messages: list[Message]) -> ChatResponse:
        """Send a plain chat request. Returns a text reply.

        Used in Phase 1 (and as a fallback in later phases where tools
        aren't needed). The returned ChatResponse will have an empty
        tool_calls list.
        """
        ...

    def chat_with_tools(
        self,
        messages: list[Message],
        tools: list[dict[str, Any]],
    ) -> ChatResponse:
        """Send a chat request with tool definitions attached.

        The LLM may respond with either text (final answer) or tool_calls
        (requests to invoke functions). The caller is responsible for
        executing tools and feeding results back via subsequent calls.

        `tools` is the list of tool schemas (see cloudseven.tools.schemas).
        """
        ...