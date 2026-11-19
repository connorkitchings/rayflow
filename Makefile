.PHONY: setup lint lint-check clean

setup:
	uv sync

lint:
	uv run ruff format .
	uv run ruff check .

lint-check:
	uv run ruff format --check .
	uv run ruff check .

clean:
	rm -rf .venv .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
