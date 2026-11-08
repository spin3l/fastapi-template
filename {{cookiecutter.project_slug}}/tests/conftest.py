import typing

import pydantic
import pytest
from dependency_injector import providers
from fastapi.testclient import TestClient

from app import di
from app.auth.application.authorization_service import AuthorizationService
from app.auth.application.service import AuthService
from app.auth.infrastructure.security.jwt_token_service import JwtTokenService
from app.main import create_app
from app.shared.config import Settings
from tests.fakes import (
    FakeFeatureFlags,
    FakeGoogleOAuthClient,
    FakePasswordHasher,
    FakeUnitOfWork,
    InMemoryResourceGrantRepository,
    InMemoryUserRepository,
)


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def settings() -> Settings:
    return Settings(
        configcat_sdk=pydantic.SecretStr("test"),
        jwt_secret=pydantic.SecretStr("test-secret-that-is-at-least-32-bytes-long"),
        google_client_id="test-client-id",
        google_client_secret=pydantic.SecretStr("test-client-secret"),
    )


@pytest.fixture
def feature_flags() -> FakeFeatureFlags:
    return FakeFeatureFlags()


@pytest.fixture
def users() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def grants() -> InMemoryResourceGrantRepository:
    return InMemoryResourceGrantRepository()


@pytest.fixture
def unit_of_work(
    users: InMemoryUserRepository,
    grants: InMemoryResourceGrantRepository,
) -> FakeUnitOfWork:
    return FakeUnitOfWork(users=users, grants=grants)


@pytest.fixture
def authorization_service(unit_of_work: FakeUnitOfWork) -> AuthorizationService:
    return AuthorizationService(uow=lambda: unit_of_work)


@pytest.fixture
def google_oauth() -> FakeGoogleOAuthClient:
    return FakeGoogleOAuthClient()


@pytest.fixture
def token_service(settings: Settings) -> JwtTokenService:
    return JwtTokenService(
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        ttl_minutes=settings.jwt_access_token_ttl_minutes,
    )


@pytest.fixture
def auth_service(
    unit_of_work: FakeUnitOfWork,
    token_service: JwtTokenService,
    google_oauth: FakeGoogleOAuthClient,
) -> AuthService:
    return AuthService(
        uow=lambda: unit_of_work,
        password_hasher=FakePasswordHasher(),
        tokens=token_service,
        google=google_oauth,
    )


@pytest.fixture
def client(
    settings: Settings,
    feature_flags: FakeFeatureFlags,
    unit_of_work: FakeUnitOfWork,
    google_oauth: FakeGoogleOAuthClient,
) -> typing.Iterator[TestClient]:
    container = di.Container()
    for resource in (container.configcat_client, container.db_engine, container.google_http_client):
        resource.override(providers.Object(None))
    container.feature_flags.override(providers.Object(feature_flags))
    container.unit_of_work.override(providers.Object(lambda: unit_of_work))
    container.password_hasher.override(providers.Object(FakePasswordHasher()))
    container.google_oauth.override(providers.Object(google_oauth))

    app = create_app(settings=settings, container=container)

    with TestClient(app) as test_client:
        yield test_client
