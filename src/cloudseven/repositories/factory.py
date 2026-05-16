"""
Repository factory.

Single place where the choice of "JSON vs API vs DB" is made. The rest of the app
calls `get_flight_repository()` and gets back something that satisfies the Protocol.

To migrate to a real backend later:
1. Implement APIFlightRepository in a new file.
2. Add an `elif settings.data_backend == "api"` branch below.
3. Done.
"""
from __future__ import annotations

from cloudseven.config import get_settings
from cloudseven.repositories.base import (
    BookingRepository,
    FlightRepository,
    LoyaltyRepository,
)
from cloudseven.repositories.json_repos import (
    JSONBookingRepository,
    JSONFlightRepository,
    JSONLoyaltyRepository,
)


def get_flight_repository() -> FlightRepository:
    settings = get_settings()
    if settings.data_backend == "json":
        return JSONFlightRepository(settings.data_dir)
    raise NotImplementedError(f"data_backend={settings.data_backend} not supported yet")


def get_booking_repository() -> BookingRepository:
    settings = get_settings()
    if settings.data_backend == "json":
        return JSONBookingRepository(settings.data_dir)
    raise NotImplementedError(f"data_backend={settings.data_backend} not supported yet")


def get_loyalty_repository() -> LoyaltyRepository:
    settings = get_settings()
    if settings.data_backend == "json":
        return JSONLoyaltyRepository(settings.data_dir)
    raise NotImplementedError(f"data_backend={settings.data_backend} not supported yet")
