import functools

import pydantic
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
    )

    configcat_sdk: pydantic.SecretStr
    configcat_poll_interval_seconds: int = 300

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/feature_flags"

    jwt_secret: pydantic.SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_ttl_minutes: int = 30

    google_client_id: str
    google_client_secret: pydantic.SecretStr
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"


@functools.cache
def get_settings() -> Settings:
    return Settings()
