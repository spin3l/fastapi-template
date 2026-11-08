from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import handlers


def test_unknown_route_uses_error_format(client: TestClient) -> None:
    response = client.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found", "code": "not_found"}


def test_validation_error_uses_error_format(client: TestClient) -> None:
    response = client.post("/auth/register", json={})

    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "validation_error"
    assert isinstance(body["detail"], list)


def test_auth_error_uses_error_format(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Bearer nope"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token", "code": "unauthorized"}
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_unhandled_exception_returns_generic_500() -> None:
    app = FastAPI()
    handlers.register_exception_handlers(app)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("secret internals")

    with TestClient(app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/boom")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error", "code": "internal_error"}
