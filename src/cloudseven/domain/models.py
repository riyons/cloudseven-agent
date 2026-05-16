"""
Core domain models.

These are the canonical shapes of CloudSeven's business entities.
Repositories return these; tools consume these; the API serializes these.

When you swap JSON for a real backend later, only the repository implementation
changes — these models stay the same. That's the point.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FlightStatus(str, Enum):
    SCHEDULED = "scheduled"
    BOARDING = "boarding"
    DEPARTED = "departed"
    IN_AIR = "in_air"
    LANDED = "landed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class CabinClass(str, Enum):
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class Flight(BaseModel):
    """A single scheduled flight."""

    flight_number: str = Field(..., examples=["CS-204"])
    origin: str = Field(..., description="IATA airport code", examples=["COK"])
    destination: str = Field(..., examples=["DXB"])
    scheduled_departure: datetime
    scheduled_arrival: datetime
    actual_departure: datetime | None = None
    actual_arrival: datetime | None = None
    status: FlightStatus = FlightStatus.SCHEDULED
    gate: str | None = None
    aircraft: str | None = Field(default=None, examples=["B737-800"])


class Passenger(BaseModel):
    """A passenger on a booking. Kept minimal — PII handling is a Phase 5 concern."""

    first_name: str
    last_name: str
    seat: str | None = None  # e.g. "14A"


class Booking(BaseModel):
    """A passenger booking (PNR)."""

    pnr: str = Field(..., examples=["ABC123"])
    passengers: list[Passenger]
    flight_number: str
    cabin_class: CabinClass = CabinClass.ECONOMY
    checked_in: bool = False
    baggage_count: int = 0


class LoyaltyAccount(BaseModel):
    """A CloudPoints loyalty account."""

    member_id: str = Field(..., examples=["CP-100042"])
    first_name: str
    last_name: str
    points_balance: int = 0
    tier: str = Field(default="Silver", examples=["Silver", "Gold", "Platinum"])
