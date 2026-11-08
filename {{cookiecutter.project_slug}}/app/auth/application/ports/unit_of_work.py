import types
import typing

from app.auth.application.ports.resource_grant_repository import ResourceGrantRepository
from app.auth.application.ports.user_repository import UserRepository


class UnitOfWork(typing.Protocol):
    """One transaction per use case: commits on a clean exit, rolls back on an exception."""

    users: UserRepository
    grants: ResourceGrantRepository

    async def __aenter__(self) -> typing.Self: ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
