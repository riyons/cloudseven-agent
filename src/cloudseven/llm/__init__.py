"""
LLM provider abstraction.

The agent calls `LLMClient.chat()` without caring whether the model is local
(Ollama) or remote (Anthropic, OpenAI). Swap by changing one env var.
"""
