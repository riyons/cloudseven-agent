"""
Tool schemas — JSON Schema descriptions of every tool the agent can call.

These schemas are what the LLM sees. They're sent on every agent turn
alongside the conversation history. The LLM uses them to decide:
  (a) whether to call a tool at all, and if so,
  (b) which tool, and
  (c) what arguments to pass.

The descriptions ARE the prompt that drives tool selection. Treat them
with the same care as the system prompt.

Schema format follows the OpenAI / Ollama convention. When we add
Anthropic support later, we'll translate at the LLM client boundary.
"""
from __future__ import annotations

from typing import Any

# ── Individual tool schemas ──────────────────────────────────────────

GET_FLIGHT_STATUS: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_flight_status",
        "description": (
            "Look up the current status and details of a single CloudSeven flight "
            "by its flight number. Use this when a passenger asks about a specific "
            "flight (e.g., 'is CS-204 on time?', 'what gate is CS-118 boarding from?', "
            "'when does CS-902 land?'). Returns scheduled departure and arrival times, "
            "status (scheduled/boarding/delayed/cancelled/landed), gate, origin, "
            "destination, and aircraft type."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "flight_number": {
                    "type": "string",
                    "description": (
                        "The CloudSeven flight number in format 'CS-NNN' "
                        "(e.g., 'CS-204', 'CS-118'). Normalize user input like "
                        "'cs204' or 'flight 204' to 'CS-204'."
                    ),
                }
            },
            "required": ["flight_number"],
            "additionalProperties": False,
        },
    },
}

SEARCH_FLIGHTS: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_flights",
        "description": (
            "Find CloudSeven flights between two airports. Use this when a passenger "
            "asks about available flights for a route (e.g., 'what flights are there "
            "from Kochi to Dubai?', 'show me flights to Mumbai'). Returns a list of "
            "matching flights with their flight numbers, times, and status. "
            "Returns an empty list if no flights match."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "origin": {
                    "type": "string",
                    "description": (
                        "Origin airport IATA code (3 letters), e.g. 'COK' for Kochi, "
                        "'BLR' for Bangalore, 'BOM' for Mumbai. Normalize city names "
                        "to codes when possible."
                    ),
                },
                "destination": {
                    "type": "string",
                    "description": (
                        "Destination airport IATA code (3 letters), e.g. 'DXB' for "
                        "Dubai, 'LHR' for London, 'SIN' for Singapore."
                    ),
                },
            },
            "required": ["origin", "destination"],
            "additionalProperties": False,
        },
    },
}

LOOKUP_BOOKING: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "lookup_booking",
        "description": (
            "Look up the details of a passenger booking by its PNR (Passenger Name "
            "Record). Use this when a passenger references a booking by its PNR "
            "(e.g., 'what's my booking ABC123?', 'check PNR XYZ789'). Returns the "
            "flight number, passenger names, cabin class, check-in status, and "
            "baggage count. Do not invent or guess PNRs — only call this when the "
            "passenger has provided one."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "pnr": {
                    "type": "string",
                    "description": (
                        "The 6-character booking reference (PNR), e.g. 'ABC123'. "
                        "Case-insensitive; will be normalized to uppercase."
                    ),
                }
            },
            "required": ["pnr"],
            "additionalProperties": False,
        },
    },
}

GET_LOYALTY_BALANCE: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "get_loyalty_balance",
        "description": (
            "Look up the CloudPoints loyalty balance and tier for a member. Use this "
            "when a passenger asks about their points or loyalty status (e.g., 'how "
            "many CloudPoints do I have?', 'what's my tier?'). The passenger must "
            "provide their member ID (format 'CP-NNNNNN'). Returns the member's name, "
            "points balance, and tier (Silver/Gold/Platinum). Do not invent member "
            "IDs — only call this when the passenger has provided one."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "member_id": {
                    "type": "string",
                    "description": (
                        "The CloudPoints member ID in format 'CP-NNNNNN' "
                        "(e.g., 'CP-100042')."
                    ),
                }
            },
            "required": ["member_id"],
            "additionalProperties": False,
        },
    },
}


# ── Registry ─────────────────────────────────────────────────────────

ALL_TOOL_SCHEMAS: list[dict[str, Any]] = [
    GET_FLIGHT_STATUS,
    SEARCH_FLIGHTS,
    LOOKUP_BOOKING,
    GET_LOYALTY_BALANCE,
]
"""The complete list of tool schemas available to the agent.

Imported by the Conversation class and passed to the LLM on every call.
To add a new tool: define its schema above, then append it here.
"""