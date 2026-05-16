.PHONY: install chat seed test lint format clean

install:
	pip install -e ".[dev]"

chat:
	python -m scripts.chat

seed:
	python -m scripts.seed_data

test:
	pytest

lint:
	ruff check src tests
	mypy src

format:
	ruff format src tests scripts
	ruff check --fix src tests scripts

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
