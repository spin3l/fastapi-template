import contextlib
import typing

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, requests, responses, status
from starlette.middleware.base import BaseHTTPMiddleware

import app.auth.infrastructure.http.dependencies as auth_dependencies
import app.auth.infrastructure.http.routes as auth_routes
import app.features.infrastructure.http.dependencies as features_dependencies
import app.{{ cookiecutter.module_name }}.infrastructure.http.routes as {{ cookiecutter.module_name }}_routes
from app import di
from app.auth.infrastructure.http import errors as auth_errors
from app.features.domain.exceptions import UnavailableFeatureError
from app.shared import config, logs


async def unavailable_feature_handler(
    _: requests.Request,
    _exc: Exception,
) -> responses.JSONResponse:
    # 404 rather than 403/503: a disabled feature looks like it doesn't exist.
    return responses.JSONResponse(
        content={"detail": "Not Found"},
        status_code=status.HTTP_404_NOT_FOUND,
    )


def create_app(
    settings: config.Settings | None = None,
    container: di.Container | None = None,
) -> FastAPI:
    if container is None:
        container = di.Container()

    if settings is not None:
        container.settings.override(settings)

    logs.setup_logging()

    container.wire(
        modules=[auth_routes, auth_dependencies, {{ cookiecutter.module_name }}_routes, features_dependencies],
    )

    @contextlib.asynccontextmanager
    async def lifespan(_: FastAPI) -> typing.AsyncGenerator[None]:
        if (init_task := container.init_resources()) is not None:
            await init_task

        yield

        if (shutdown_task := container.shutdown_resources()) is not None:
            await shutdown_task

    app = FastAPI(
        lifespan=lifespan,
        title="{{ cookiecutter.project_name }}",
        docs_url="/docs",
    )
    app.state.container = container

    app.add_middleware(BaseHTTPMiddleware, dispatch=logs.logging_middleware)
    app.add_middleware(CorrelationIdMiddleware)  # Must be after `logging_middleware`

    app.include_router(auth_routes.router)
    app.include_router({{ cookiecutter.module_name }}_routes.router)

    app.add_exception_handler(UnavailableFeatureError, unavailable_feature_handler)
    auth_errors.register_exception_handlers(app)

    return app
