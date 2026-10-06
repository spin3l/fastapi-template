import httpx
import structlog
from configcatclient.configcatclient import ConfigCatClient
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.auth.application.ports.google_oauth import GoogleOAuthClient
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.token_service import TokenService
from app.auth.application.ports.user_repository import UserRepository
from app.auth.application.service import AuthService
from app.auth.infrastructure.google.oauth_client import GoogleOAuthHttpClient, create_http_client
from app.auth.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyUserRepository
from app.auth.infrastructure.security.jwt_token_service import JwtTokenService
from app.auth.infrastructure.security.password_hasher import PwdlibPasswordHasher
from app.features.application.ports.feature_flags import FeatureFlagProvider
from app.features.infrastructure.configcat import ConfigCatFeatureFlags, create_configcat_client
from app.{{ cookiecutter.module_name }}.application.ports.{{ cookiecutter.entity_name }}_repository import {{ cookiecutter.__entity_class }}Repository
from app.{{ cookiecutter.module_name }}.application.service import {{ cookiecutter.__entity_class }}Service
from app.{{ cookiecutter.module_name }}.infrastructure.persistence.in_memory import InMemory{{ cookiecutter.__entity_class }}Repository
from app.shared import config, db, logs


class Container(containers.DeclarativeContainer):
    settings: providers.Singleton[config.Settings] = providers.Singleton(
        config.get_settings,
    )

    logger: providers.Singleton[structlog.stdlib.BoundLogger] = providers.Singleton(
        logs.create_logger,
    )

    # Resources, will cleanup
    configcat_client: providers.Resource[ConfigCatClient] = providers.Resource(
        create_configcat_client,
        sdk=settings.provided.configcat_sdk,
        poll_interval_seconds=settings.provided.configcat_poll_interval_seconds,
    )

    db_engine: providers.Resource[AsyncEngine] = providers.Resource(
        db.create_engine,
        database_url=settings.provided.database_url,
    )

    google_http_client: providers.Resource[httpx.AsyncClient] = providers.Resource(
        create_http_client,
    )

    session_factory: providers.Singleton[async_sessionmaker[AsyncSession]] = providers.Singleton(
        db.create_session_factory,
        engine=db_engine,
    )

    # Auth
    users_repository: providers.Singleton[UserRepository] = providers.Singleton(
        SqlAlchemyUserRepository,
        session_factory=session_factory,
    )

    password_hasher: providers.Singleton[PasswordHasher] = providers.Singleton(
        PwdlibPasswordHasher,
    )

    token_service: providers.Singleton[TokenService] = providers.Singleton(
        JwtTokenService,
        secret=settings.provided.jwt_secret,
        algorithm=settings.provided.jwt_algorithm,
        ttl_minutes=settings.provided.jwt_access_token_ttl_minutes,
    )

    google_oauth: providers.Singleton[GoogleOAuthClient] = providers.Singleton(
        GoogleOAuthHttpClient,
        http=google_http_client,
        client_id=settings.provided.google_client_id,
        client_secret=settings.provided.google_client_secret,
        redirect_uri=settings.provided.google_redirect_uri,
    )

    auth_service: providers.Factory[AuthService] = providers.Factory(
        AuthService,
        users=users_repository,
        password_hasher=password_hasher,
        tokens=token_service,
        google=google_oauth,
    )

    # Features
    feature_flags: providers.Singleton[FeatureFlagProvider] = providers.Singleton(
        ConfigCatFeatureFlags,
        client=configcat_client,
    )

    # {{ cookiecutter.__module_title }}
    {{ cookiecutter.entity_name }}_repository: providers.Singleton[{{ cookiecutter.__entity_class }}Repository] = providers.Singleton(
        InMemory{{ cookiecutter.__entity_class }}Repository,
    )

    {{ cookiecutter.entity_name }}_service: providers.Factory[{{ cookiecutter.__entity_class }}Service] = providers.Factory(
        {{ cookiecutter.__entity_class }}Service,
        repository={{ cookiecutter.entity_name }}_repository,
    )
