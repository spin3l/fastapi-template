import dataclasses

from app.auth.application.ports.google_oauth import GoogleOAuthClient
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.token_service import TokenService
from app.auth.application.ports.user_repository import UserRepository
from app.auth.domain.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    InvalidTokenError,
    UnverifiedEmailError,
)
from app.auth.domain.user import User, normalize_email


@dataclasses.dataclass(frozen=True, slots=True)
class AuthService:
    users: UserRepository
    password_hasher: PasswordHasher
    tokens: TokenService
    google: GoogleOAuthClient

    async def register(self, email: str, full_name: str, password: str) -> User:
        email = normalize_email(email)
        if await self.users.get_by_email(email) is not None:
            raise EmailAlreadyRegisteredError()

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=await self.password_hasher.hash(password),
        )
        return await self.users.add(user)

    async def login(self, email: str, password: str) -> str:
        user = await self.users.get_by_email(normalize_email(email))

        if user is None or user.hashed_password is None:
            # Spend the same time as a real check so response timing doesn't reveal
            # which emails are registered.
            await self.password_hasher.hash(password)
            raise InvalidCredentialsError()

        if not await self.password_hasher.verify(password, user.hashed_password):
            raise InvalidCredentialsError()

        return self._issue_token(user)

    async def authenticate(self, token: str) -> User:
        user = await self.users.get_by_id(self.tokens.verify(token))
        if user is None:
            raise InvalidTokenError()

        user.ensure_can_login()
        return user

    def google_authorization_url(self, state: str) -> str:
        return self.google.authorization_url(state)

    async def login_with_google(self, code: str) -> str:
        identity = await self.google.fetch_identity(code)
        if not identity.email_verified:
            raise UnverifiedEmailError()

        user = await self.users.get_by_google_subject(identity.subject)

        if user is None:
            email = normalize_email(identity.email)
            user = await self.users.get_by_email(email)

            if user is None:
                user = await self.users.add(
                    User(
                        email=email,
                        full_name=identity.full_name,
                        google_subject=identity.subject,
                    )
                )
            else:
                user.link_google_account(identity.subject)
                user = await self.users.update(user)

        return self._issue_token(user)

    def _issue_token(self, user: User) -> str:
        user.ensure_can_login()
        if user.id is None:
            raise ValueError("Cannot issue a token for a user that hasn't been persisted")

        return self.tokens.issue(user.id)
