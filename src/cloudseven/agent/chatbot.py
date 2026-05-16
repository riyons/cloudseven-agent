"""
Phase 1 chatbot: a stateful conversation wrapper around an LLMClient.

This is deliberately a class rather than a free function — when we add LangGraph
in Phase 3, we can swap the internals while keeping `Conversation.send()` as
the public interface. The scripts/chat.py CLI doesn't have to change at all.
"""
from __future__ import annotations

from cloudseven.agent.prompts import CLOUDSEVEN_ASSISTANT_PROMPT
from cloudseven.llm.base import LLMClient, Message
from cloudseven.logging_config import get_logger

log = get_logger(__name__)


class Conversation:
    """Maintains conversation history and dispatches to the LLM."""

    def __init__(
        self,
        llm: LLMClient,
        system_prompt: str = CLOUDSEVEN_ASSISTANT_PROMPT,
    ) -> None:
        self._llm = llm
        self._system_prompt = system_prompt
        self._messages: list[Message] = [
            Message(role="system", content=system_prompt),
        ]

    def send(self, user_message: str) -> str:
        """Send a user message and return the assistant reply."""
        self._messages.append(Message(role="user", content=user_message))
        log.info("user_message_sent", chars=len(user_message))

        response = self._llm.chat(self._messages)
        assistant_reply = response["content"]

        self._messages.append(Message(role="assistant", content=assistant_reply))
        log.info(
            "assistant_reply",
            chars=len(assistant_reply),
            input_tokens=response.get("input_tokens"),
            output_tokens=response.get("output_tokens"),
        )
        return assistant_reply

    def reset(self) -> None:
        """Clear conversation history but keep the system prompt."""
        self._messages = [Message(role="system", content=self._system_prompt)]
        log.info("conversation_reset")

    @property
    def message_count(self) -> int:
        """Number of messages excluding the system prompt."""
        return len(self._messages) - 1
