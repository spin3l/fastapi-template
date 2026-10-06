.PHONY: dev test lint format typecheck check hooks pre-commit migrate migration db up down

dev:
	uv run uvicorn app.main:create_app --factory --reload

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run lint-imports

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy app tests

check: lint typecheck test

hooks:
	uv run pre-commit install

pre-commit:
	uv run pre-commit run --all-files

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(m)"

db:
	docker compose up -d --wait db

up:
	docker compose up -d --build --wait api

down:
	docker compose down
