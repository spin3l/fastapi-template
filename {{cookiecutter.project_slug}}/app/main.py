import contextlib
import typing

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

import app.auth.infrastructure.http.admin_routes as auth_admin_routes
import app.auth.infrastructure.http.dependencies as auth_dependencies
import app.auth.infrastructure.http.routes as auth_routes
import app.features.infrastructure.http.dependencies as features_dependencies

# Sorted separately so the import order doesn't depend on the module name.
# isort: split
import app.{{ cookiecutter.module_name }}.infrastructure.http.routes as {{ cookiecutter.module_name }}_routes
from app import di, handlers
from app.shared import config, logs
from app.shared.http import health


def create_app(
    settings: config.Settings | None = None,
    container: di.Container | None = None,
) -> FastAPI:
    if container is None:
        container = di.Container()

    if settings is not None:
        container.settings.override(settings)

    settings = container.settings()
    logs.setup_logging(level=settings.log_level, log_format=settings.log_format)

    container.wire(
        modules=[
            auth_routes,
            auth_admin_routes,
            auth_dependencies,
            {{ cookiecutter.module_name }}_routes,
            features_dependencies,
            health,
        ],
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
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.container = container

    app.add_middleware(BaseHTTPMiddleware, dispatch=logs.logging_middleware)
    app.add_middleware(CorrelationIdMiddleware)  # Must be after `logging_middleware`
    if settings.cors_origins:
        # Added last so it's the outermost middleware and answers preflights itself.
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["X-Request-ID"],
        )

    app.include_router(health.router)
    app.include_router(auth_routes.router)
    app.include_router(auth_admin_routes.router)
    app.include_router({{ cookiecutter.module_name }}_routes.router)

    handlers.register_exception_handlers(app)

    return app
