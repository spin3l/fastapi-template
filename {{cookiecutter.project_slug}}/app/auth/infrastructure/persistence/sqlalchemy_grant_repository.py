import dataclasses
import typing

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.ports.resource_grant_repository import ResourceGrantRepository
from app.auth.domain.roles import ResourceGrant
from app.auth.infrastructure.persistence.orm import ResourceGrantModel


@dataclasses.dataclass(frozen=True, slots=True)
class SqlAlchemyResourceGrantRepository(ResourceGrantRepository):
    """Runs inside a `SqlAlchemyUnitOfWork` session; it flushes but never commits."""

    session: AsyncSession

    @typing.override
    async def exists(self, grant: ResourceGrant) -> bool:
        return await self.session.get(ResourceGrantModel, self._key(grant)) is not None

    @typing.override
    async def list_for_user(self, user_id: int) -> list[ResourceGrant]:
        models = await self.session.scalars(
            select(ResourceGrantModel)
            .where(ResourceGrantModel.user_id == user_id)
            .order_by(ResourceGrantModel.resource_type, ResourceGrantModel.resource_id),
        )
        return [model.to_domain() for model in models]

    @typing.override
    async def add(self, grant: ResourceGrant) -> None:
        await self.session.merge(ResourceGrantModel.from_domain(grant))
        await self.session.flush()

    @typing.override
    async def delete(self, grant: ResourceGrant) -> None:
        if (model := await self.session.get(ResourceGrantModel, self._key(grant))) is not None:
            await self.session.delete(model)
            await self.session.flush()

    @typing.override
    async def delete_for_user(self, user_id: int) -> None:
        await self.session.execute(
            delete(ResourceGrantModel).where(ResourceGrantModel.user_id == user_id),
        )

    @staticmethod
    def _key(grant: ResourceGrant) -> tuple[int, str, str]:
        return (grant.user_id, grant.resource_type, grant.resource_id)
