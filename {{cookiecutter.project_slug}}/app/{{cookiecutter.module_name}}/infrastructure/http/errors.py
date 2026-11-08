from fastapi import FastAPI, requests, responses, status

import app.shared.http.errors as shared_errors
from app.{{ cookiecutter.module_name }}.domain import exceptions

_STATUS_CODES: dict[type[Exception], int] = {
    exceptions.{{ cookiecutter.__entity_class }}NotFoundError: status.HTTP_404_NOT_FOUND,
}


async def {{ cookiecutter.entity_name }}_error_handler(
    _: requests.Request,
    exc: Exception,
) -> responses.Response:
    status_code = _STATUS_CODES.get(type(exc), status.HTTP_400_BAD_REQUEST)
    return shared_errors.error_response(status_code, str(exc))


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exceptions.{{ cookiecutter.__entity_class }}Error,
        {{ cookiecutter.entity_name }}_error_handler,
    )
