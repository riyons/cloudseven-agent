"""
Tool function implementations.

Each function here is the executable side of a schema declared in `schemas.py`.
The two files stay in lockstep:
  - schemas.py declares names, descriptions, and parameter shapes for the LLM.
  - functions.py implements the actual behaviour using our repositories.

Design rules:
- Every function has the signature `f(arguments: dict, *, repo) -> dict`.
- Arguments are validated; bad input raises ValueError (the executor turns
  this into a structured error for the LLM).
- "Not found" cases return a structured error dict — they are normal outcomes
  the LLM can handle, not exceptions to surface to the user.
- Returned dicts are JSON-safe (`mode="json"`) so they can be embedded in
  the next LLM call's message history.
"""
from __future__ import annotations

from typing import Any

from cloudseven.domain.exceptions import (
    BookingNotFoundError,
    FlightNotFoundError,
    LoyaltyAccountNotFoundError,
)
from cloudseven.logging_config import get_logger
from cloudseven.repositories.base import (
    BookingRepository,
    FlightRepository,
    LoyaltyRepository,
)

log = get_logger(__name__)


def get_flight_status(
    arguments: dict[str, Any],
    *,
    repo: FlightRepository,
) -> dict[str, Any]:
    """Look up a single flight by number. Backs the get_flight_status schema."""
    flight_number = _require_str(arguments, "flight_number")
    log.info("tool_call", tool="get_flight_status", flight_number=flight_number)

    try:
        flight = repo.get_by_number(flight_number)
    except FlightNotFoundError:
        return {
            "error": "flight_not_found",
            "message": (
                f"No flight with number '{flight_number}' was found. "
                f"Please verify the flight number with the passenger."
            ),
        }

    return flight.model_dump(mode="json")


def search_flights(
    arguments: dict[str, Any],
    *,
    repo: FlightRepository,
) -> dict[str, Any]:
    """Find flights between two airports. Backs the search_flights schema."""
    origin = _require_str(arguments, "origin").upper()
    destination = _require_str(arguments, "destination").upper()
    log.info("tool_call", tool="search_flights", origin=origin, destination=destination)

    flights = repo.search(origin=origin, destination=destination)
    return {
        "origin": origin,
        "destination": destination,
        "count": len(flights),
        "flights": [f.model_dump(mode="json") for f in flights],
    }


def lookup_booking(
    arguments: dict[str, Any],
    *,
    repo: BookingRepository,
) -> dict[str, Any]:
    """Look up a booking by PNR. Backs the lookup_booking schema."""
    pnr = _require_str(arguments, "pnr").upper()
    log.info("tool_call", tool="lookup_booking", pnr=pnr)

    try:
        booking = repo.get_by_pnr(pnr)
    except BookingNotFoundError:
        return {
            "error": "booking_not_found",
            "message": (
                f"No booking with PNR '{pnr}' was found. "
                f"Please ask the passenger to verify their booking reference."
            ),
        }

    return booking.model_dump(mode="json")


def get_loyalty_balance(
    arguments: dict[str, Any],
    *,
    repo: LoyaltyRepository,
) -> dict[str, Any]:
    """Look up loyalty account by member ID. Backs the get_loyalty_balance schema."""
    member_id = _require_str(arguments, "member_id")
    log.info("tool_call", tool="get_loyalty_balance", member_id=member_id)

    try:
        account = repo.get_by_member_id(member_id)
    except LoyaltyAccountNotFoundError:
        return {
            "error": "loyalty_account_not_found",
            "message": (
                f"No loyalty account with member ID '{member_id}' was found. "
                f"Please ask the passenger to verify their CloudPoints member ID."
            ),
        }

    return account.model_dump(mode="json")


# ── Helpers ──────────────────────────────────────────────────────────


def _require_str(arguments: dict[str, Any], key: str) -> str:
    """Pull a required string argument out of the LLM-supplied dict.

    Tools must never trust the shape of `arguments` blindly — the LLM
    could omit a key, pass None, or pass a non-string. This helper
    raises a clear ValueError that the executor will catch and surface
    back to the LLM as a structured error.
    """
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Tool called without a valid '{key}' argument. "
            f"Got: {value!r}. Please provide a non-empty string."
        )
    return value.strip()