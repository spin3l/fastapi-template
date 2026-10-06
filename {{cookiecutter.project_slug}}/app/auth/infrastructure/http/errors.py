from fastapi import FastAPI, requests, responses, status

from app.auth.domain.exceptions import (
    AuthError,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    UnverifiedEmailError,
)

_STATUS_CODES: dict[type[Exception], int] = {
    EmailAlreadyRegisteredError: status.HTTP_409_CONFLICT,
    InactiveUserError: status.HTTP_403_FORBIDDEN,
    UnverifiedEmailError: status.HTTP_403_FORBIDDEN,
}


async def auth_error_handler(_: requests.Request, exc: Exception) -> responses.JSONResponse:
    status_code = _STATUS_CODES.get(type(exc), status.HTTP_401_UNAUTHORIZED)
    headers = {"WWW-Authenticate": "Bearer"} if status_code == 401 else None

    return responses.JSONResponse(
        content={"detail": str(exc)},
        status_code=status_code,
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AuthError, auth_error_handler)
