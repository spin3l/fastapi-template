from fastapi import FastAPI

import app.{{ cookiecutter.module_name }}.infrastructure.http.errors as {{ cookiecutter.module_name }}_errors
from app.auth.infrastructure.http import errors as auth_errors
from app.features.infrastructure.http import errors as features_errors
from app.shared.http import errors as shared_errors


def register_exception_handlers(app: FastAPI) -> None:
    """Register the generic handlers, then each module's `infrastructure/http/errors.py`.

    Starlette matches handlers by the exception's MRO, so a module handler for `AuthError` wins
    over the generic `Exception` one regardless of registration order.
    """
    shared_errors.register_exception_handlers(app)
    auth_errors.register_exception_handlers(app)
    features_errors.register_exception_handlers(app)
    {{ cookiecutter.module_name }}_errors.register_exception_handlers(app)
