"""
Tool executor — dispatches LLM tool calls to the right Python function.

This module is the bridge between the LLM's JSON-shaped intent
("call get_flight_status with {flight_number: 'CS-204'}") and our
actual Python tool functions backed by repositories.

It does three things:
  1. Looks up the requested tool by name.
  2. Calls the tool function with its required repository.
  3. Catches every possible failure mode and returns a structured
     error dict the LLM can read on the next turn.

Tool calls must NEVER crash the agent loop. Every exception is caught
and converted into a result the LLM can use to recover.
"""
from __future__ import annotations

from typing import Any, Callable

from cloudseven.logging_config import get_logger
from cloudseven.repositories.base import (
    BookingRepository,
    FlightRepository,
    LoyaltyRepository,
)
from cloudseven.tools.functions import (
    get_flight_status,
    get_loyalty_balance,
    lookup_booking,
    search_flights,
)

log = get_logger(__name__)


# A tool entry tells the executor:
#   - which function to call
#   - which repository attribute on the executor to pass as `repo`
#
# The second item is a string (the attribute name) rather than the repo
# itself so that the registry can be defined statically at module load
# time, before any ToolExecutor instance exists.
_ToolEntry = tuple[Callable[..., dict[str, Any]], str]


_TOOL_REGISTRY: dict[str, _ToolEntry] = {
    "get_flight_status": (get_flight_status, "_flight_repo"),
    "search_flights": (search_flights, "_flight_repo"),
    "lookup_booking": (lookup_booking, "_booking_repo"),
    "get_loyalty_balance": (get_loyalty_balance, "_loyalty_repo"),
}


class ToolExecutor:
    """Dispatches tool calls from the LLM to the appropriate Python function.

    Construct once at app startup with the three repositories. Call
    `execute(tool_name, arguments)` for each tool call the LLM makes.
    The return value is always a JSON-safe dict — either the tool's
    result or a structured error.
    """

    def __init__(
        self,
        flight_repo: FlightRepository,
        booking_repo: BookingRepository,
        loyalty_repo: LoyaltyRepository,
    ) -> None:
        self._flight_repo = flight_repo
        self._booking_repo = booking_repo
        self._loyalty_repo = loyalty_repo

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Run a single tool call and return its result (or a structured error).

        Never raises. All failure modes produce a dict with an `error` key.
        """
        entry = _TOOL_REGISTRY.get(tool_name)
        if entry is None:
            log.warning(
                "tool_not_found",
                tool=tool_name,
                available=list(_TOOL_REGISTRY.keys()),
            )
            return {
                "error": "tool_not_found",
                "message": (
                    f"No tool named '{tool_name}' is available. "
                    f"Available tools: {', '.join(_TOOL_REGISTRY.keys())}."
                ),
            }

        func, repo_attr = entry
        repo = getattr(self, repo_attr)

        try:
            return func(arguments, repo=repo)
        except ValueError as e:
            # Raised by _require_str when arguments are missing/empty.
            # Structured so the LLM can correct and retry.
            log.info("tool_bad_arguments", tool=tool_name, error=str(e))
            return {
                "error": "invalid_arguments",
                "message": str(e),
            }
        except Exception as e:
            # Catch-all for unexpected failures. We log with full traceback
            # so we can debug, but return a generic message to the LLM —
            # internal errors should never leak to the model verbatim.
            log.exception(
                "tool_execution_failed",
                tool=tool_name,
                arguments=arguments,
                error=str(e),
            )
            return {
                "error": "tool_execution_failed",
                "message": (
                    f"The tool '{tool_name}' failed unexpectedly. "
                    f"Please try a different approach or escalate to a human agent."
                ),
            }