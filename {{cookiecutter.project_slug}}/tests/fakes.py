import dataclasses
import itertools
import typing

import pydantic

from app.auth.application.ports.google_oauth import GoogleIdentity, GoogleOAuthClient
from app.auth.application.ports.password_hasher import PasswordHasher
from app.auth.application.ports.user_repository import UserRepository
from app.auth.domain.exceptions import IdentityProviderError
from app.auth.domain.user import User
from app.features.application.ports.feature_flags import FeatureFlagProvider


@dataclasses.dataclass
class FakeFeatureFlags(FeatureFlagProvider):
    flags: dict[str, typing.Any] = dataclasses.field(default_factory=dict)

    @typing.override
    def get_value[T: pydantic.BaseModel | str | bool](self, feature_name: str, default: T) -> T:
        return typing.cast(T, self.flags.get(feature_name, default))


@dataclasses.dataclass
class InMemoryUserRepository(UserRepository):
    users: dict[int, User] = dataclasses.field(default_factory=dict)
    _ids: "itertools.count[int]" = dataclasses.field(default_factory=lambda: itertools.count(1))

    @typing.override
    async def get_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    @typing.override
    async def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)

    @typing.override
    async def get_by_google_subject(self, subject: str) -> User | None:
        return next((u for u in self.users.values() if u.google_subject == subject), None)

    @typing.override
    async def add(self, user: User) -> User:
        user.id = next(self._ids)
        self.users[user.id] = user
        return user

    @typing.override
    async def update(self, user: User) -> User:
        assert user.id is not None
        self.users[user.id] = user
        return user


class FakePasswordHasher(PasswordHasher):
    @typing.override
    async def hash(self, password: str) -> str:
        return f"hashed:{password}"

    @typing.override
    async def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed:{password}"


@dataclasses.dataclass
class FakeGoogleOAuthClient(GoogleOAuthClient):
    identities: dict[str, GoogleIdentity] = dataclasses.field(default_factory=dict)

    @typing.override
    def authorization_url(self, state: str) -> str:
        return f"https://accounts.google.test/auth?state={state}"

    @typing.override
    async def fetch_identity(self, code: str) -> GoogleIdentity:
        try:
            return self.identities[code]
        except KeyError:
            raise IdentityProviderError() from None
