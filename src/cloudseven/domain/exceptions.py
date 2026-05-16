"""Custom domain exceptions. Use these instead of generic ValueError."""
from __future__ import annotations


class CloudSevenError(Exception):
    """Base exception for all domain errors."""


class NotFoundError(CloudSevenError):
    """Entity not found in the repository."""


class FlightNotFoundError(NotFoundError):
    """Flight number doesn't exist."""


class BookingNotFoundError(NotFoundError):
    """PNR doesn't exist."""


class LoyaltyAccountNotFoundError(NotFoundError):
    """Loyalty member ID doesn't exist."""


class LLMError(CloudSevenError):
    """LLM call failed."""
