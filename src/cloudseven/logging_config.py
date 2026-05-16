"""
Structured logging setup using structlog.

Why structured logging matters:
- In dev, you get pretty colored output.
- In prod, you get JSON logs that can be parsed by log aggregators (Loki, Datadog, CloudWatch).
- Every log line can carry context (user_id, request_id, route, etc.) without string formatting.

Usage:
    from cloudseven.logging_config import get_logger
    log = get_logger(__name__)
    log.info("user_message_received", user_id="u123", length=len(msg))
"""
from __future__ import annotations

import logging
import sys

import structlog

from cloudseven.config import get_settings


def configure_logging() -> None:
    """Configure stdlib logging + structlog. Call once at app startup."""
    settings = get_settings()

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=settings.log_level,
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if settings.log_format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a logger. Call configure_logging() once before using."""
    return structlog.get_logger(name)
