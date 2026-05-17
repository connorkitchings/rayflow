.PHONY: setup test lint docs clean

setup:
	uv sync --extra dev --extra lighting
	uv run pre-commit install

test:
	uv run pytest

lint:
	uv run ruff format .
	uv run ruff check .

lint-check:
	uv run ruff format --check .
	uv run ruff check .

docs:
	uv run mkdocs serve

docs-build:
	uv run mkdocs build --strict

clean:
	rm -rf .venv
	rm -rf site
	rm -rf htmlcov
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
