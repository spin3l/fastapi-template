import asyncio
import typing

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, responses, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.di import Container
from app.shared import logs
from app.shared.http.errors import error_response

READY_TIMEOUT_SECONDS = 2

router = APIRouter(include_in_schema=False)


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: the process is up and serving. Never touches dependencies."""
    return {"status": "ok"}


@router.get("/ready", response_model=None)
@inject
async def ready(
    engine: typing.Annotated[AsyncEngine, Depends(Provide[Container.db_engine])],
) -> responses.Response:
    """Readiness: the database answers, so the instance can take traffic."""
    try:
        async with asyncio.timeout(READY_TIMEOUT_SECONDS), engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception as exc:
        logs.logger.warning("readiness_check_failed", error=repr(exc))
        return error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Database unavailable",
        )

    return responses.JSONResponse({"status": "ok"})
