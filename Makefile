.PHONY: reproduce install test lint type-check format clean help

help:
	@echo "RAF Development Commands"
	@echo "======================="
	@echo ""
	@echo "reproduce        Run quick reproducibility validation (~3-5 min)"
	@echo "reproduce-full   Run full reproducibility validation (~30-45 min)"
	@echo "install          Install all dependencies with pinned versions (uv sync --all-extras)"
	@echo "test             Run all tests with coverage"
	@echo "test-quick       Run tests in quick mode (subset, < 1 min)"
	@echo "lint             Run ruff linter"
	@echo "type-check       Run mypy strict type checking"
	@echo "format           Format code with black and isort"
	@echo "clean            Remove cache and build artifacts"
	@echo ""

install:
	uv sync --all-extras

reproduce:
	uv sync --all-extras
	python examples/empirical_validation.py --mode quick

reproduce-full:
	uv sync --all-extras
	python examples/empirical_validation.py --mode full

test:
	uv run pytest tests/ -v --cov=raf --cov-report=term-missing --cov-fail-under=40

test-quick:
	uv run pytest tests/ -v --cov=raf -x

lint:
	uv run ruff check raf tests

type-check:
	uv run mypy raf/ --strict

format:
	uv run black raf/ tests/
	uv run isort raf/ tests/

clean:
	rm -rf .pytest_cache .coverage .mypy_cache htmlcov build/ dist/ *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
