import dataclasses
import typing

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.ports.user_repository import UserRepository
from app.auth.domain.exceptions import EmailAlreadyRegisteredError
from app.auth.domain.user import User
from app.auth.infrastructure.persistence.orm import UserModel


@dataclasses.dataclass(frozen=True, slots=True)
class SqlAlchemyUserRepository(UserRepository):
    """Runs inside a `SqlAlchemyUnitOfWork` session; it flushes but never commits."""

    session: AsyncSession

    @typing.override
    async def get_by_id(self, user_id: int) -> User | None:
        return await self._get_one(select(UserModel).where(UserModel.id == user_id))

    @typing.override
    async def get_by_email(self, email: str) -> User | None:
        return await self._get_one(select(UserModel).where(UserModel.email == email))

    @typing.override
    async def get_by_google_subject(self, subject: str) -> User | None:
        return await self._get_one(select(UserModel).where(UserModel.google_subject == subject))

    @typing.override
    async def add(self, user: User) -> User:
        model = UserModel.from_domain(user)
        self.session.add(model)
        await self._flush()
        return model.to_domain()

    @typing.override
    async def update(self, user: User) -> User:
        model = await self.session.merge(UserModel.from_domain(user))
        await self._flush()
        return model.to_domain()

    async def _get_one(self, statement: Select[tuple[UserModel]]) -> User | None:
        model = await self.session.scalar(statement)
        return model.to_domain() if model else None

    async def _flush(self) -> None:
        # The service checks for duplicates first, but two concurrent requests can both pass that
        # check; the unique constraints are the real guarantee. `email` is the only unique column a
        # password signup sets; a `google_subject` clash means two concurrent first Google logins,
        # for which a 409 is fine too.
        try:
            await self.session.flush()
        except IntegrityError as exc:
            raise EmailAlreadyRegisteredError() from exc
