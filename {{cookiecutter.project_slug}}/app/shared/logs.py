import collections.abc
import logging
import time
import typing

import structlog
from asgi_correlation_id import correlation_id
from fastapi import requests, responses


def create_logger() -> structlog.stdlib.BoundLogger:
    return typing.cast(structlog.stdlib.BoundLogger, structlog.get_logger("{{ cookiecutter.__project_snake }}"))


logger = create_logger()


def setup_logging() -> None:
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)

    for name in ("uvicorn", "uvicorn.error", "configcat"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True


async def logging_middleware(
    request: requests.Request,
    call_next: collections.abc.Callable[[requests.Request], typing.Awaitable[responses.Response]],
) -> responses.Response:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(asgi_correlation_id=correlation_id.get())

    start_time = time.perf_counter()
    response = await call_next(request)
    response_time = time.perf_counter() - start_time

    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        response_time=f"{response_time:.3f}s",
    )

    return response
