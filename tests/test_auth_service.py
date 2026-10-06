import pytest

from app.auth.application.ports.google_oauth import GoogleIdentity
from app.auth.application.service import AuthService
from app.auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    UnverifiedEmailError,
)
from app.auth.domain.user import User
from tests.fakes import FakeGoogleOAuthClient, InMemoryUserRepository

pytestmark = pytest.mark.anyio


async def test_register_normalizes_email_and_hashes_password(auth_service: AuthService) -> None:
    user = await auth_service.register(" Ada@Example.com ", "Ada", "s3cret-pass")

    assert user.id is not None
    assert user.email == "ada@example.com"
    assert user.hashed_password == "hashed:s3cret-pass"


async def test_register_rejects_duplicate_email(auth_service: AuthService) -> None:
    await auth_service.register("ada@example.com", "Ada", "s3cret-pass")

    with pytest.raises(EmailAlreadyRegisteredError):
        await auth_service.register("ADA@example.com", "Ada", "other-pass")


async def test_login_returns_token_for_valid_credentials(auth_service: AuthService) -> None:
    user = await auth_service.register("ada@example.com", "Ada", "s3cret-pass")

    token = await auth_service.login("ada@example.com", "s3cret-pass")

    assert await auth_service.authenticate(token) == user


@pytest.mark.parametrize(
    ("email", "password"),
    [("ada@example.com", "wrong-pass"), ("nobody@example.com", "s3cret-pass")],
)
async def test_login_rejects_bad_credentials(
    auth_service: AuthService, email: str, password: str
) -> None:
    await auth_service.register("ada@example.com", "Ada", "s3cret-pass")

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(email, password)


async def test_login_rejects_inactive_user(
    auth_service: AuthService, users: InMemoryUserRepository
) -> None:
    user = await auth_service.register("ada@example.com", "Ada", "s3cret-pass")
    user.is_active = False

    with pytest.raises(InactiveUserError):
        await auth_service.login("ada@example.com", "s3cret-pass")


async def test_authenticate_rejects_token_for_deleted_user(
    auth_service: AuthService, users: InMemoryUserRepository
) -> None:
    await auth_service.register("ada@example.com", "Ada", "s3cret-pass")
    token = await auth_service.login("ada@example.com", "s3cret-pass")
    users.users.clear()

    with pytest.raises(InvalidTokenError):
        await auth_service.authenticate(token)


def _identity(email_verified: bool = True) -> GoogleIdentity:
    return GoogleIdentity(
        subject="google-123",
        email="Ada@Example.com",
        email_verified=email_verified,
        full_name="Ada",
    )


async def test_google_login_creates_user_without_password(
    auth_service: AuthService,
    google_oauth: FakeGoogleOAuthClient,
) -> None:
    google_oauth.identities["code"] = _identity()

    user = await auth_service.authenticate(await auth_service.login_with_google("code"))

    assert user.email == "ada@example.com"
    assert user.google_subject == "google-123"
    assert user.hashed_password is None


async def test_google_login_links_existing_account_by_email(
    auth_service: AuthService,
    google_oauth: FakeGoogleOAuthClient,
    users: InMemoryUserRepository,
) -> None:
    existing = await auth_service.register("ada@example.com", "Ada", "s3cret-pass")
    google_oauth.identities["code"] = _identity()

    user = await auth_service.authenticate(await auth_service.login_with_google("code"))

    assert user.id == existing.id
    assert user.google_subject == "google-123"
    assert len(users.users) == 1


async def test_google_login_rejects_unverified_email(
    auth_service: AuthService,
    google_oauth: FakeGoogleOAuthClient,
) -> None:
    google_oauth.identities["code"] = _identity(email_verified=False)

    with pytest.raises(UnverifiedEmailError):
        await auth_service.login_with_google("code")


async def test_password_login_fails_for_google_only_user(
    auth_service: AuthService,
    users: InMemoryUserRepository,
) -> None:
    await users.add(User(email="ada@example.com", full_name="Ada", google_subject="google-123"))

    with pytest.raises(InvalidCredentialsError):
        await auth_service.login("ada@example.com", "anything")
