import dataclasses

import pydantic
import pytest

from app.auth.domain.exceptions import InvalidTokenError
from app.auth.infrastructure.security.jwt_token_service import JwtTokenService


def test_issued_token_round_trips(token_service: JwtTokenService) -> None:
    assert token_service.verify(token_service.issue(42)) == 42


def test_expired_token_is_rejected(token_service: JwtTokenService) -> None:
    expired = dataclasses.replace(token_service, ttl_minutes=-1)

    with pytest.raises(InvalidTokenError):
        token_service.verify(expired.issue(42))


def test_token_signed_with_other_secret_is_rejected(token_service: JwtTokenService) -> None:
    other = dataclasses.replace(
        token_service, secret=pydantic.SecretStr("another-secret-that-is-32-bytes-long!")
    )

    with pytest.raises(InvalidTokenError):
        token_service.verify(other.issue(42))


def test_garbage_token_is_rejected(token_service: JwtTokenService) -> None:
    with pytest.raises(InvalidTokenError):
        token_service.verify("not-a-jwt")
