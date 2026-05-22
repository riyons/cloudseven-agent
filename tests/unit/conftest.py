"""
Shared test fixtures for the tool layer.

This file provides fake repositories backed by in-memory data, plus a
ToolExecutor wired with all three. Tests import these by name as function
arguments — pytest discovers and injects them automatically.

The fakes mirror the real Pydantic models from domain/, so tests catch type
mismatches if the domain layer ever changes. They satisfy the same Protocol
interfaces as the JSON repositories (FlightRepository, BookingRepository,
LoyaltyRepository) without ever touching disk.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cloudseven.domain.exceptions import (
    BookingNotFoundError,
    FlightNotFoundError,
    LoyaltyAccountNotFoundError,
)
from cloudseven.domain.models import (
    Booking,
    Flight,
    LoyaltyAccount,
    Passenger,
)
from cloudseven.tools.executor import ToolExecutor


# ── Fake flight repository ──────────────────────────────────────────


class FakeFlightRepository:
    """In-memory FlightRepository backed by a dict of test flights."""

    def __init__(self, flights: list[Flight]) -> None:
        self._flights = {f.flight_number: f for f in flights}

    def get_by_number(self, flight_number: str) -> Flight:
        try:
            return self._flights[flight_number]
        except KeyError:
            raise FlightNotFoundError(
                f"Flight {flight_number} not found"
            ) from None

    def search(self, origin: str, destination: str) -> list[Flight]:
        return [
            f
            for f in self._flights.values()
            if f.origin == origin and f.destination == destination
        ]


# ── Fake booking repository ─────────────────────────────────────────


class FakeBookingRepository:
    """In-memory BookingRepository backed by a dict of test bookings."""

    def __init__(self, bookings: list[Booking]) -> None:
        self._bookings = {b.pnr: b for b in bookings}

    def get_by_pnr(self, pnr: str) -> Booking:
        try:
            return self._bookings[pnr]
        except KeyError:
            raise BookingNotFoundError(f"Booking {pnr} not found") from None


# ── Fake loyalty repository ─────────────────────────────────────────


class FakeLoyaltyRepository:
    """In-memory LoyaltyRepository backed by a dict of test accounts."""

    def __init__(self, accounts: list[LoyaltyAccount]) -> None:
        self._accounts = {a.member_id: a for a in accounts}

    def get_by_member_id(self, member_id: str) -> LoyaltyAccount:
        try:
            return self._accounts[member_id]
        except KeyError:
            raise LoyaltyAccountNotFoundError(
                f"Member {member_id} not found"
            ) from None


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def fake_flight_repo() -> FakeFlightRepository:
    """A FlightRepository with three known flights for testing."""
    flights = [
        Flight(
            flight_number="CS-204",
            origin="COK",
            destination="DXB",
            scheduled_departure=datetime(2026, 5, 16, 2, 30, tzinfo=timezone.utc),
            scheduled_arrival=datetime(2026, 5, 16, 5, 15, tzinfo=timezone.utc),
            status="scheduled",
            gate="C12",
            aircraft="B737-800",
        ),
        Flight(
            flight_number="CS-118",
            origin="BLR",
            destination="BOM",
            scheduled_departure=datetime(2026, 5, 16, 9, 0, tzinfo=timezone.utc),
            scheduled_arrival=datetime(2026, 5, 16, 11, 0, tzinfo=timezone.utc),
            status="scheduled",
            gate="A4",
            aircraft="A320",
        ),
        Flight(
            flight_number="CS-902",
            origin="COK",
            destination="DXB",
            scheduled_departure=datetime(2026, 5, 17, 14, 0, tzinfo=timezone.utc),
            scheduled_arrival=datetime(2026, 5, 17, 16, 45, tzinfo=timezone.utc),
            status="scheduled",
            gate="C8",
            aircraft="B737-800",
        ),
    ]
    return FakeFlightRepository(flights)


@pytest.fixture
def fake_booking_repo() -> FakeBookingRepository:
    """A BookingRepository with two known bookings for testing."""
    bookings = [
        Booking(
            pnr="ABC123",
            flight_number="CS-204",
            passengers=[
                Passenger(first_name="Test", last_name="Passenger"),
            ],
            cabin_class="economy",
            checked_in=False,
            baggage_count=2,
        ),
        Booking(
            pnr="XYZ789",
            flight_number="CS-118",
            passengers=[
                Passenger(first_name="Another", last_name="Passenger"),
                Passenger(first_name="Second", last_name="Passenger"),
            ],
            cabin_class="business",
            checked_in=True,
            baggage_count=4,
        ),
    ]
    return FakeBookingRepository(bookings)


@pytest.fixture
def fake_loyalty_repo() -> FakeLoyaltyRepository:
    """A LoyaltyRepository with two known accounts for testing."""
    accounts = [
        LoyaltyAccount(
            member_id="CP-100042",
            first_name="Test",
            last_name="Member",
            points_balance=24500,
            tier="Gold",
        ),
        LoyaltyAccount(
            member_id="CP-100043",
            first_name="Other",
            last_name="Member",
            points_balance=5000,
            tier="Silver",
        ),
    ]
    return FakeLoyaltyRepository(accounts)


@pytest.fixture
def executor(
    fake_flight_repo: FakeFlightRepository,
    fake_booking_repo: FakeBookingRepository,
    fake_loyalty_repo: FakeLoyaltyRepository,
) -> ToolExecutor:
    """A ToolExecutor wired with all three fake repositories."""
    return ToolExecutor(
        flight_repo=fake_flight_repo,
        booking_repo=fake_booking_repo,
        loyalty_repo=fake_loyalty_repo,
    )
