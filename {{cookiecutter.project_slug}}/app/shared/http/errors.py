import http
import typing

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, exceptions, requests, responses, status
from fastapi.encoders import jsonable_encoder
from starlette.exceptions import HTTPException

from app.shared import logs
from app.shared.http.schemas import BaseSchema


class ErrorResponse(BaseSchema):
    detail: str | list[typing.Any]
    code: str


def default_code(status_code: int) -> str:
    return http.HTTPStatus(status_code).phrase.lower().replace(" ", "_").replace("-", "_")


def error_response(
    status_code: int,
    detail: str | list[typing.Any],
    *,
    code: str | None = None,
    headers: typing.Mapping[str, str] | None = None,
) -> responses.JSONResponse:
    """Build every error response through here so all errors share the same body."""
    body = ErrorResponse(detail=detail, code=code or default_code(status_code))
    return responses.JSONResponse(
        content=body.model_dump(by_alias=True),
        status_code=status_code,
        headers=headers,
    )


async def http_exception_handler(_: requests.Request, exc: Exception) -> responses.Response:
    # Starlette's HTTPException (FastAPI's subclasses it) also covers routing 404s/405s.
    assert isinstance(exc, HTTPException)
    return error_response(exc.status_code, exc.detail, headers=exc.headers)


async def validation_exception_handler(_: requests.Request, exc: Exception) -> responses.Response:
    assert isinstance(exc, exceptions.RequestValidationError)
    return error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        jsonable_encoder(exc.errors()),
        code="validation_error",
    )


async def unhandled_exception_handler(_: requests.Request, exc: Exception) -> responses.Response:
    # Runs in ServerErrorMiddleware, outside CorrelationIdMiddleware, so the request id header
    # has to be added by hand.
    logs.logger.exception("unhandled_exception", exc_info=exc)
    request_id = correlation_id.get()
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Internal Server Error",
        code="internal_error",
        headers={"X-Request-ID": request_id} if request_id else None,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(exceptions.RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
