"""
Unit tests for the ToolExecutor in cloudseven.tools.executor.

The executor's contract: given a tool name and arguments, return a dict.
Never raise. The three error categories must all surface as structured
error dicts that the LLM can use to recover gracefully.

Tests cover:
- Happy path dispatch to each of the four tools
- Routing to the correct repository (validates getattr indirection)
- The three error categories: tool_not_found, invalid_arguments, tool_execution_failed
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch


# ── Happy path dispatch ─────────────────────────────────────────────


class TestExecutorDispatch:
    def test_dispatches_get_flight_status_correctly(self, executor):
        result = executor.execute(
            "get_flight_status",
            {"flight_number": "CS-204"},
        )

        assert result["flight_number"] == "CS-204"
        assert result["origin"] == "COK"
        assert "error" not in result

    def test_dispatches_search_flights_correctly(self, executor):
        result = executor.execute(
            "search_flights",
            {"origin": "COK", "destination": "DXB"},
        )

        assert result["count"] == 2
        assert result["origin"] == "COK"
        assert "error" not in result

    def test_dispatches_lookup_booking_correctly(self, executor):
        result = executor.execute(
            "lookup_booking",
            {"pnr": "ABC123"},
        )

        assert result["pnr"] == "ABC123"
        assert result["flight_number"] == "CS-204"
        assert "error" not in result

    def test_dispatches_get_loyalty_balance_correctly(self, executor):
        result = executor.execute(
            "get_loyalty_balance",
            {"member_id": "CP-100042"},
        )

        assert result["member_id"] == "CP-100042"
        assert result["points_balance"] == 24500
        assert "error" not in result


# ── Routing to the correct repository ───────────────────────────────


class TestExecutorRepositoryRouting:
    """Verify that tools receive the right repository (getattr indirection)."""

    def test_flight_tools_receive_flight_repo(
        self, executor, fake_flight_repo
    ):
        # If flight tools didn't use the flight repo, this lookup would fail
        result = executor.execute(
            "get_flight_status",
            {"flight_number": "CS-118"},
        )
        assert result["origin"] == "BLR"

    def test_booking_tools_receive_booking_repo(
        self, executor, fake_booking_repo
    ):
        # XYZ789 only exists in the fake booking repo, not anywhere else
        result = executor.execute(
            "lookup_booking",
            {"pnr": "XYZ789"},
        )
        assert result["pnr"] == "XYZ789"
        assert result["cabin_class"] == "business"

    def test_loyalty_tools_receive_loyalty_repo(
        self, executor, fake_loyalty_repo
    ):
        # CP-100043 only exists in the fake loyalty repo
        result = executor.execute(
            "get_loyalty_balance",
            {"member_id": "CP-100043"},
        )
        assert result["points_balance"] == 5000
        assert result["tier"] == "Silver"


# ── Error category 1: tool_not_found ────────────────────────────────


class TestExecutorToolNotFound:
    def test_unknown_tool_returns_error_dict(self, executor):
        result = executor.execute("nonexistent_tool", {})

        assert result["error"] == "tool_not_found"
        assert "nonexistent_tool" in result["message"]

    def test_unknown_tool_message_lists_available_tools(self, executor):
        result = executor.execute("book_a_taxi", {})

        # All four tool names should appear in the error message
        assert "get_flight_status" in result["message"]
        assert "search_flights" in result["message"]
        assert "lookup_booking" in result["message"]
        assert "get_loyalty_balance" in result["message"]

    def test_unknown_tool_does_not_raise(self, executor):
        # Should never raise — this is the executor's contract
        result = executor.execute("hallucinated_tool", {"foo": "bar"})
        assert isinstance(result, dict)


# ── Error category 2: invalid_arguments ─────────────────────────────


class TestExecutorInvalidArguments:
    def test_missing_argument_returns_error_dict(self, executor):
        # get_flight_status requires flight_number
        result = executor.execute("get_flight_status", {})

        assert result["error"] == "invalid_arguments"
        assert "flight_number" in result["message"]

    def test_empty_string_argument_returns_error_dict(self, executor):
        result = executor.execute("lookup_booking", {"pnr": ""})

        assert result["error"] == "invalid_arguments"
        assert "pnr" in result["message"]

    def test_invalid_arguments_does_not_raise(self, executor):
        # ValueError from tool functions must be caught
        result = executor.execute("get_loyalty_balance", {})
        assert isinstance(result, dict)
        assert result["error"] == "invalid_arguments"


# ── Error category 3: tool_execution_failed (catch-all) ─────────────


# ── Error category 3: tool_execution_failed (catch-all) ─────────────


class TestExecutorUnexpectedFailure:
    """The executor must catch any unexpected exception from a tool.

    We force this by temporarily replacing a tool function in the registry
    with one that raises RuntimeError.
    """

    def test_unexpected_exception_returns_generic_error(self, executor):
        def failing_tool(arguments, *, repo):
            raise RuntimeError("simulated unexpected failure")

        with patch.dict(
            "cloudseven.tools.executor._TOOL_REGISTRY",
            {"get_flight_status": (failing_tool, "_flight_repo")},
        ):
            result = executor.execute(
                "get_flight_status",
                {"flight_number": "CS-204"},
            )

        assert result["error"] == "tool_execution_failed"
        assert "get_flight_status" in result["message"]

    def test_unexpected_exception_does_not_leak_internals(self, executor):
        def leaky_tool(arguments, *, repo):
            raise RuntimeError("database connection string: secret123")

        with patch.dict(
            "cloudseven.tools.executor._TOOL_REGISTRY",
            {"get_flight_status": (leaky_tool, "_flight_repo")},
        ):
            result = executor.execute(
                "get_flight_status",
                {"flight_number": "CS-204"},
            )

        # The secret value from the exception should not be in the message
        assert "secret123" not in result["message"]
        assert "database connection string" not in result["message"]

    def test_unexpected_exception_does_not_raise(self, executor):
        def anything_tool(arguments, *, repo):
            raise Exception("anything")

        with patch.dict(
            "cloudseven.tools.executor._TOOL_REGISTRY",
            {"lookup_booking": (anything_tool, "_booking_repo")},
        ):
            result = executor.execute("lookup_booking", {"pnr": "ABC123"})
            assert isinstance(result, dict)
