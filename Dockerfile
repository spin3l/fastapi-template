# syntax=docker/dockerfile:1

# Builder: resolve the locked dependencies into a virtualenv with uv.
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /code

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev --no-install-project


# Runtime: same Python base, only the virtualenv and the source code.
FROM python:3.13-slim-trixie

RUN groupadd --system app && useradd --system --gid app --no-create-home app

WORKDIR /code

COPY --from=builder /code/.venv /code/.venv
COPY alembic.ini ./
COPY app ./app

ENV PATH="/code/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

USER app

EXPOSE 8000

# Exec form so the server receives SIGTERM and runs the lifespan shutdown.
# `fastapi run` can't call an app factory, so use uvicorn directly.
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
