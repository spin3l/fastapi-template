import collections.abc
import contextlib
import typing

import pytest
from dependency_injector import providers
from fastapi import FastAPI
from fastapi.testclient import TestClient


class _FakeConnection:
    async def execute(self, _: typing.Any) -> None:
        return None


@typing.final
class _FakeEngine:
    def __init__(self, *, reachable: bool) -> None:
        self.reachable = reachable

    @contextlib.asynccontextmanager
    async def connect(self) -> collections.abc.AsyncIterator[_FakeConnection]:
        if not self.reachable:
            raise OSError("connection refused")
        yield _FakeConnection()


def _use_engine(client: TestClient, engine: _FakeEngine) -> None:
    app = typing.cast(FastAPI, client.app)
    app.state.container.db_engine.override(providers.Object(engine))


def test_health_is_ok_without_dependencies(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("reachable", "status_code"),
    [(True, 200), (False, 503)],
)
def test_ready_reflects_database(client: TestClient, reachable: bool, status_code: int) -> None:
    _use_engine(client, _FakeEngine(reachable=reachable))

    response = client.get("/ready")

    assert response.status_code == status_code
