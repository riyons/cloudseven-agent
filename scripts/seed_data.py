"""
Seed script — regenerates fake JSON data files.

Phase 1: pre-populated files in data/ are hand-edited.
Phase 2+: this script can be extended to generate larger, more realistic
fake datasets (e.g. 200 flights, 50 bookings) using Faker.

Run with: python -m scripts.seed_data
"""
from __future__ import annotations

import sys


def main() -> int:
    print("Seed script — not yet implemented.")
    print("Phase 1 uses hand-edited files in data/. This will be filled in Phase 2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
