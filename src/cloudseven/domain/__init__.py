"""
Domain layer — pure business types.

Rules for this package:
- No I/O (no file reads, no HTTP, no DB).
- No framework imports (no FastAPI, no LangGraph).
- Only Pydantic for validation and Python stdlib.

This is the stable core. Everything else depends on it; it depends on nothing.
"""
