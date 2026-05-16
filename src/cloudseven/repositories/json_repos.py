"""
JSON file-backed repositories.

These read flat JSON files from `data/`. Suitable for development and demos.
For production: replace with API-backed or DB-backed implementations
following the same Protocol contracts in `base.py`.

Note: these load files lazily on first access and cache in memory.
For real production use, you'd want proper caching with TTL and refresh.
"""
from __future__ import annotations

import json
from pathlib import Path

from cloudseven.domain.exceptions import (
    BookingNotFoundError,
    FlightNotFoundError,
    LoyaltyAccountNotFoundError,
)
from cloudseven.domain.models import Booking, Flight, LoyaltyAccount


class JSONFlightRepository:
    """Reads flights from data/flights.json."""

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / "flights.json"
        self._cache: dict[str, Flight] | None = None

    def _load(self) -> dict[str, Flight]:
        if self._cache is None:
            raw = json.loads(self._path.read_text())
            self._cache = {item["flight_number"]: Flight(**item) for item in raw}
        return self._cache

    def get_by_number(self, flight_number: str) -> Flight:
        flights = self._load()
        if flight_number not in flights:
            raise FlightNotFoundError(f"Flight {flight_number} not found")
        return flights[flight_number]

    def search(self, origin: str, destination: str) -> list[Flight]:
        flights = self._load()
        return [
            f
            for f in flights.values()
            if f.origin.upper() == origin.upper()
            and f.destination.upper() == destination.upper()
        ]


class JSONBookingRepository:
    """Reads bookings from data/bookings.json."""

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / "bookings.json"
        self._cache: dict[str, Booking] | None = None

    def _load(self) -> dict[str, Booking]:
        if self._cache is None:
            raw = json.loads(self._path.read_text())
            self._cache = {item["pnr"]: Booking(**item) for item in raw}
        return self._cache

    def get_by_pnr(self, pnr: str) -> Booking:
        bookings = self._load()
        key = pnr.upper()
        if key not in bookings:
            raise BookingNotFoundError(f"Booking {pnr} not found")
        return bookings[key]


class JSONLoyaltyRepository:
    """Reads loyalty accounts from data/loyalty.json."""

    def __init__(self, data_dir: Path) -> None:
        self._path = data_dir / "loyalty.json"
        self._cache: dict[str, LoyaltyAccount] | None = None

    def _load(self) -> dict[str, LoyaltyAccount]:
        if self._cache is None:
            raw = json.loads(self._path.read_text())
            self._cache = {item["member_id"]: LoyaltyAccount(**item) for item in raw}
        return self._cache

    def get_by_member_id(self, member_id: str) -> LoyaltyAccount:
        accounts = self._load()
        if member_id not in accounts:
            raise LoyaltyAccountNotFoundError(f"Member {member_id} not found")
        return accounts[member_id]
