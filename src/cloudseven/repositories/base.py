"""
Abstract repository interfaces (Protocols).

Why Protocol instead of ABC?
- Protocols give structural typing — any class with matching methods satisfies them,
  no inheritance required. This is more flexible and explicit.
- Better for testing: fakes don't need to inherit, they just need the right shape.

Every method here is what the tools layer will call. When you replace JSON with
a real API, you implement these same methods against the API client.
"""
from __future__ import annotations

from typing import Protocol

from cloudseven.domain.models import Booking, Flight, LoyaltyAccount


class FlightRepository(Protocol):
    """Read access to flights."""

    def get_by_number(self, flight_number: str) -> Flight:
        """Return the flight or raise FlightNotFoundError."""
        ...

    def search(self, origin: str, destination: str) -> list[Flight]:
        """Return flights matching the given route. May be empty."""
        ...


class BookingRepository(Protocol):
    """Read access to bookings (PNRs)."""

    def get_by_pnr(self, pnr: str) -> Booking:
        """Return the booking or raise BookingNotFoundError."""
        ...


class LoyaltyRepository(Protocol):
    """Read access to loyalty accounts."""

    def get_by_member_id(self, member_id: str) -> LoyaltyAccount:
        """Return the account or raise LoyaltyAccountNotFoundError."""
        ...
