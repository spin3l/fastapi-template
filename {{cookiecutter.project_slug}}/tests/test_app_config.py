import pytest
from fastapi.testclient import TestClient

from app.shared.config import Settings

ORIGIN = "https://app.example.com"


@pytest.fixture
def settings(settings: Settings) -> Settings:
    return settings.model_copy(update={"cors_origins": [ORIGIN], "docs_enabled": False})


def test_cors_preflight_allows_configured_origin(client: TestClient) -> None:
    response = client.options(
        "/auth/me",
        headers={"Origin": ORIGIN, "Access-Control-Request-Method": "GET"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == ORIGIN


def test_cors_rejects_unknown_origin(client: TestClient) -> None:
    response = client.get("/health", headers={"Origin": "https://evil.example.com"})

    assert "access-control-allow-origin" not in response.headers


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_docs_can_be_disabled(client: TestClient, path: str) -> None:
    assert client.get(path).status_code == 404
