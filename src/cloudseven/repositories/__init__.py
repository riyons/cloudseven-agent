"""
Repository layer — data access abstraction.

The agent and tools depend on the abstract interfaces in `base.py`,
never on a concrete implementation. To swap JSON for a real API:
1. Add a new file (e.g., `api_repos.py`) implementing the same protocols.
2. Update `factory.py` to return the new implementation.
3. Done — zero changes anywhere else.
"""
