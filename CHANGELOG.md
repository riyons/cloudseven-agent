# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2026-05-22

### Added

- Unit test suite for the Phase 2 tool layer (33 tests, runs in ~20ms):
  - `tests/unit/conftest.py` with fake repositories and pytest fixtures
  - `tests/unit/test_tool_functions.py` covering all four tool functions
  - `tests/unit/test_tool_executor.py` covering dispatch and the three
    error categories
- Fake repositories satisfy the same Protocol interfaces as the JSON
  implementations, validating that Phase 1's interface-based design
  enables testing without I/O.

### Notes

- Closes the test-suite deliverable that was deferred from v0.2.0
- Phase 3 (LangGraph + semantic routing + LangSmith) begins from this tag

## [0.2.0] - 2026-05-18

### Added

- Phase 2 — Tool calling (ReAct loop)
  - Four tool schemas in OpenAI-compatible function-calling format:
    `get_flight_status`, `search_flights`, `lookup_booking`,
    `get_loyalty_balance`
  - Tool implementations with uniform signature `(arguments, *, repo) -> dict`,
    returning errors as structured data rather than raising
  - `ToolExecutor` class with static registry mapping tool names to
    (function, repository attribute) pairs; resolves repositories dynamically
    via `getattr` at execution time
  - Three-category error handling in the executor: `tool_not_found`,
    `invalid_arguments`, `tool_execution_failed`
  - `LLMClient.chat_with_tools()` method on the LLM Protocol; new `ToolCall`
    TypedDict for structured tool-call requests
  - `Message.role` extended with `"tool"` for tool result messages
  - ReAct loop inside `Conversation.send()` with iteration cap of 5
  - Graceful fallback message when iteration cap is exceeded
  - Wire-format translation between internal `ToolCall` shape and Ollama's
    nested `function` shape
- Updated system prompt (`agent/prompts.py`) for tool-aware Sevi:
  capability-level descriptions of available tools, explicit guidance on
  when to use them, and a rule for tool-error responses
- `phase2-observations.md` in `docs/` — manual evaluation with before/after
  comparison against Phase 1
- Python reference guide PDF (`docs/CloudSeven_Python_Reference.pdf`,
  112 pages) covering the type system, Pydantic, production patterns, and
  errors/logging used throughout the codebase

### Changed

- `Conversation` now requires a `ToolExecutor` at construction; CLI
  composition root (`scripts/chat.py`) wires three repositories into the
  executor at startup
- `Conversation._messages` widened from `list[Message]` to
  `list[dict[str, Any]]` to accommodate Ollama's message shapes for
  tool-call requests and tool results

### Notes

- Test suite for the tool layer is deferred to v0.2.1, before Phase 3 begins
- See `docs/phase2-observations.md` for an honest evaluation of what Phase 2
  improved (real flight/booking/loyalty lookups, graceful tool-error handling)
  and what remains unaddressed (policy hallucinations — slated for Phase 4
  RAG)

## [0.1.0] - 2026-05-16

### Added

- Phase 1 — Foundation
  - Project scaffold with src layout
  - Configuration module using pydantic-settings
  - Structured logging with structlog
  - Domain models (Flight, Booking, Passenger, LoyaltyAccount)
  - Repository pattern with JSON-backed implementations
  - LLM abstraction layer with Ollama client
  - Conversation class with multi-turn memory
  - CLI entry point (`python -m scripts.chat`)
  - Seed data: flights, bookings, loyalty accounts, policy markdown
  - Learning guide PDF in `docs/`
  - MIT License
  - Code of Conduct (Contributor Covenant 2.1)
  - Contributing guidelines

### Fixed

- Use `structlog.stdlib.LoggerFactory` instead of `PrintLoggerFactory` so the `add_logger_name` processor works (`PrintLogger` has no `.name` attribute).

[Unreleased]: https://github.com/riyons/cloudseven-agent/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/riyons/cloudseven-agent/releases/tag/v0.2.1
[0.2.0]: https://github.com/riyons/cloudseven-agent/releases/tag/v0.2.0
[0.1.0]: https://github.com/riyons/cloudseven-agent/releases/tag/v0.1.0