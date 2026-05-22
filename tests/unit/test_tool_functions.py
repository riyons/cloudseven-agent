"""
Unit tests for the four tool functions in cloudseven.tools.functions.

Each function is tested for:
- Happy path: valid input returns the expected data shape
- Not-found path: missing data returns a structured error dict (no exception)
- Argument validation: missing required fields raise ValueError

Tests use fake repositories from conftest.py — no JSON files, no I/O,
no LLM calls. Should run in well under a second total.
"""
from __future__ import annotations

import pytest

from cloudseven.tools.functions import (
    get_flight_status,
    get_loyalty_balance,
    lookup_booking,
    search_flights,
)


# ── get_flight_status ───────────────────────────────────────────────


class TestGetFlightStatus:
    def test_returns_flight_data_for_known_flight(self, fake_flight_repo):
        result = get_flight_status(
            {"flight_number": "CS-204"},
            repo=fake_flight_repo,
        )

        assert result["flight_number"] == "CS-204"
        assert result["origin"] == "COK"
        assert result["destination"] == "DXB"
        assert result["gate"] == "C12"
        assert result["status"] == "scheduled"
        assert "error" not in result

    def test_returns_error_dict_for_unknown_flight(self, fake_flight_repo):
        result = get_flight_status(
            {"flight_number": "CS-999"},
            repo=fake_flight_repo,
        )

        assert result["error"] == "flight_not_found"
        assert "CS-999" in result["message"]

    def test_raises_value_error_for_missing_flight_number(self, fake_flight_repo):
        with pytest.raises(ValueError, match="flight_number"):
            get_flight_status({}, repo=fake_flight_repo)

    def test_raises_value_error_for_empty_flight_number(self, fake_flight_repo):
        with pytest.raises(ValueError, match="flight_number"):
            get_flight_status({"flight_number": ""}, repo=fake_flight_repo)

    def test_raises_value_error_for_non_string_flight_number(self, fake_flight_repo):
        with pytest.raises(ValueError, match="flight_number"):
            get_flight_status({"flight_number": 204}, repo=fake_flight_repo)


# ── search_flights ──────────────────────────────────────────────────


class TestSearchFlights:
    def test_returns_matching_flights(self, fake_flight_repo):
        result = search_flights(
            {"origin": "COK", "destination": "DXB"},
            repo=fake_flight_repo,
        )

        assert result["origin"] == "COK"
        assert result["destination"] == "DXB"
        assert result["count"] == 2  # CS-204 and CS-902 both COK -> DXB
        assert len(result["flights"]) == 2

    def test_returns_empty_list_when_no_matches(self, fake_flight_repo):
        result = search_flights(
            {"origin": "COK", "destination": "SIN"},
            repo=fake_flight_repo,
        )

        assert result["origin"] == "COK"
        assert result["destination"] == "SIN"
        assert result["count"] == 0
        assert result["flights"] == []

    def test_uppercases_lowercase_input(self, fake_flight_repo):
        # The tool function normalizes case via .upper()
        result = search_flights(
            {"origin": "cok", "destination": "dxb"},
            repo=fake_flight_repo,
        )

        assert result["origin"] == "COK"
        assert result["destination"] == "DXB"
        assert result["count"] == 2

    def test_raises_value_error_for_missing_origin(self, fake_flight_repo):
        with pytest.raises(ValueError, match="origin"):
            search_flights({"destination": "DXB"}, repo=fake_flight_repo)

    def test_raises_value_error_for_missing_destination(self, fake_flight_repo):
        with pytest.raises(ValueError, match="destination"):
            search_flights({"origin": "COK"}, repo=fake_flight_repo)


# ── lookup_booking ──────────────────────────────────────────────────


class TestLookupBooking:
    def test_returns_booking_data_for_known_pnr(self, fake_booking_repo):
        result = lookup_booking({"pnr": "ABC123"}, repo=fake_booking_repo)

        assert result["pnr"] == "ABC123"
        assert result["flight_number"] == "CS-204"
        assert result["cabin_class"] == "economy"
        assert result["checked_in"] is False
        assert "error" not in result

    def test_normalizes_lowercase_pnr(self, fake_booking_repo):
        # The tool function uppercases PNRs before lookup
        result = lookup_booking({"pnr": "abc123"}, repo=fake_booking_repo)

        assert result["pnr"] == "ABC123"
        assert "error" not in result

    def test_returns_error_dict_for_unknown_pnr(self, fake_booking_repo):
        result = lookup_booking({"pnr": "ZZZ999"}, repo=fake_booking_repo)

        assert result["error"] == "booking_not_found"
        assert "ZZZ999" in result["message"]

    def test_raises_value_error_for_missing_pnr(self, fake_booking_repo):
        with pytest.raises(ValueError, match="pnr"):
            lookup_booking({}, repo=fake_booking_repo)


# ── get_loyalty_balance ─────────────────────────────────────────────


class TestGetLoyaltyBalance:
    def test_returns_account_data_for_known_member(self, fake_loyalty_repo):
        result = get_loyalty_balance(
            {"member_id": "CP-100042"},
            repo=fake_loyalty_repo,
        )

        assert result["member_id"] == "CP-100042"
        assert result["points_balance"] == 24500
        assert result["tier"] == "Gold"
        assert "error" not in result

    def test_returns_error_dict_for_unknown_member(self, fake_loyalty_repo):
        result = get_loyalty_balance(
            {"member_id": "CP-999999"},
            repo=fake_loyalty_repo,
        )

        assert result["error"] == "loyalty_account_not_found"
        assert "CP-999999" in result["message"]

    def test_raises_value_error_for_missing_member_id(self, fake_loyalty_repo):
        with pytest.raises(ValueError, match="member_id"):
            get_loyalty_balance({}, repo=fake_loyalty_repo)
