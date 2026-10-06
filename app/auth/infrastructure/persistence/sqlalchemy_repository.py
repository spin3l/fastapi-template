import dataclasses
import typing

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.application.ports.user_repository import UserRepository
from app.auth.domain.user import User
from app.auth.infrastructure.persistence.orm import UserModel


@dataclasses.dataclass(frozen=True, slots=True)
class SqlAlchemyUserRepository(UserRepository):
    session_factory: async_sessionmaker[AsyncSession]

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
        async with self.session_factory.begin() as session:
            model = UserModel.from_domain(user)
            session.add(model)
            await session.flush()
            return model.to_domain()

    @typing.override
    async def update(self, user: User) -> User:
        async with self.session_factory.begin() as session:
            model = await session.merge(UserModel.from_domain(user))
            await session.flush()
            return model.to_domain()

    async def _get_one(self, statement: Select[tuple[UserModel]]) -> User | None:
        async with self.session_factory() as session:
            model = await session.scalar(statement)
            return model.to_domain() if model else None
