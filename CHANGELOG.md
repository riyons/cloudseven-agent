# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/<your-username>/cloudseven-agent/compare/HEAD
