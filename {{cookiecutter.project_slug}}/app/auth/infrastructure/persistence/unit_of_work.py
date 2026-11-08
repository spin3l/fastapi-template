import types
import typing

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.auth.application.ports.resource_grant_repository import ResourceGrantRepository
from app.auth.application.ports.unit_of_work import UnitOfWork
from app.auth.application.ports.user_repository import UserRepository
from app.auth.infrastructure.persistence.sqlalchemy_grant_repository import (
    SqlAlchemyResourceGrantRepository,
)
from app.auth.infrastructure.persistence.sqlalchemy_repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    users: UserRepository
    grants: ResourceGrantRepository

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    @typing.override
    async def __aenter__(self) -> typing.Self:
        self._session = self._session_factory()
        self.users = SqlAlchemyUserRepository(session=self._session)
        self.grants = SqlAlchemyResourceGrantRepository(session=self._session)
        return self

    @typing.override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        assert self._session is not None, "Use the unit of work as `async with`"
        try:
            if exc_type is None:
                await self._session.commit()
            else:
                await self._session.rollback()
        finally:
            await self._session.close()
            self._session = None
