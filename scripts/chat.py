"""
CLI entry point. Run with:
    python -m scripts.chat
or:
    make chat
"""
from __future__ import annotations

import sys

from cloudseven.agent.chatbot import Conversation
from cloudseven.config import get_settings
from cloudseven.llm.factory import get_llm_client
from cloudseven.logging_config import configure_logging, get_logger

log = get_logger(__name__)


def main() -> int:
    configure_logging()
    settings = get_settings()

    model_name = (
        settings.ollama_model
        if settings.llm_provider == "ollama"
        else settings.anthropic_model
    )
    log.info(
        "starting_chat",
        provider=settings.llm_provider,
        model=model_name,
        env=settings.app_env,
    )

    llm = get_llm_client()
    conversation = Conversation(llm=llm)

    print("\n" + "=" * 60)
    print("  CloudSeven Airlines  —  Sevi Assistant")
    print(f"  Provider: {settings.llm_provider}  |  Env: {settings.app_env}")
    print("  Commands: 'exit' to quit, 'reset' to clear history")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nGoodbye, safe travels!\n")
            return 0

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("\nGoodbye, safe travels!\n")
            return 0
        if user_input.lower() == "reset":
            conversation.reset()
            print("[history cleared]\n")
            continue

        try:
            reply = conversation.send(user_input)
        except Exception as e:  # noqa: BLE001 — top-level catch for CLI
            log.exception("chat_error")
            print(f"\n[error] {e}\n")
            continue

        print(f"\nSevi: {reply}\n")


if __name__ == "__main__":
    sys.exit(main())
