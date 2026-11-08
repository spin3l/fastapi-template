from fastapi import FastAPI, requests, responses, status

from app.features.domain.exceptions import UnavailableFeatureError
from app.shared.http.errors import error_response


async def unavailable_feature_handler(_: requests.Request, _exc: Exception) -> responses.Response:
    # 404 rather than 403/503: a disabled feature looks like it doesn't exist.
    return error_response(status.HTTP_404_NOT_FOUND, "Not Found")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UnavailableFeatureError, unavailable_feature_handler)
