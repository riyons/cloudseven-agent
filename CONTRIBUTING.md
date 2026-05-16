# Contributing to CloudSeven Agent

Thanks for your interest! This is primarily a **personal learning project**
built in public, but contributions, suggestions, and feedback are welcome.

## Ways to contribute

- **Bug reports** — open an issue with reproduction steps.
- **Suggestions** — open a discussion or issue tagged `enhancement`.
- **Documentation improvements** — typo fixes, clarifications, examples.
- **Code contributions** — see "Development workflow" below.

## Development workflow

1. **Fork & clone**

   ```bash
   git clone https://github.com/<your-username>/cloudseven-agent.git
   cd cloudseven-agent
   ```

2. **Set up the environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   cp .env.example .env
   ```

3. **Create a branch**

   ```bash
   git checkout -b feat/your-feature-name
   ```

4. **Make changes & format**

   ```bash
   make format    # ruff format + auto-fix
   make lint      # ruff + mypy
   make test      # pytest
   ```

5. **Commit using Conventional Commits**

   ```
   feat: add support for booking lookup tool
   fix: handle empty PNR gracefully
   docs: clarify Phase 2 setup steps
   refactor: extract retrieval logic
   test: add unit tests for routing
   chore: bump dependencies
   ```

6. **Open a pull request** with a clear description of what changed and why.

## Code style

- Python 3.11+
- Type hints on every function signature
- Pydantic models for data shapes
- `ruff` for linting and formatting (config in `pyproject.toml`)
- `mypy` for static type checking

## Code of Conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
By participating, you agree to abide by its terms.

## Questions

Open a GitHub Discussion or reach out via the contact info in the main README.
