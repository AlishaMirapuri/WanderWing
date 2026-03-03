.PHONY: help install dev-install api frontend test test-unit test-integration test-cov lint format typecheck check db-init db-migrate db-upgrade db-downgrade seed clean

help:
	@echo "WanderWing Development Commands"
	@echo "================================"
	@echo "install          Install production dependencies"
	@echo "dev-install      Install development dependencies"
	@echo "api              Run FastAPI server"
	@echo "frontend         Run Streamlit frontend"
	@echo "test             Run all tests"
	@echo "test-unit        Run unit tests only"
	@echo "test-integration Run integration tests only"
	@echo "test-cov         Run tests with coverage report"
	@echo "lint             Run ruff linter"
	@echo "format           Format code with ruff and black"
	@echo "typecheck        Run mypy type checker"
	@echo "check            Run all quality checks"
	@echo "db-init          Initialize database"
	@echo "db-migrate       Create new migration"
	@echo "db-upgrade       Apply migrations"
	@echo "db-downgrade     Rollback last migration"
	@echo "seed             Seed database with test data"
	@echo "clean            Remove generated files"

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

api:
	uvicorn wanderwing.api.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	streamlit run src/wanderwing/frontend/app.py --server.port 8501

test:
	pytest tests/

test-unit:
	pytest tests/unit/

test-integration:
	pytest tests/integration/

test-cov:
	pytest --cov=src/wanderwing --cov-report=html --cov-report=term

lint:
	ruff check src/ tests/

format:
	ruff check --fix src/ tests/
	black src/ tests/

typecheck:
	mypy src/wanderwing

check: lint typecheck test

db-init:
	alembic upgrade head

db-migrate:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

db-upgrade:
	alembic upgrade head

db-downgrade:
	alembic downgrade -1

seed:
	python scripts/seed_data.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov dist build
	rm -f .coverage
