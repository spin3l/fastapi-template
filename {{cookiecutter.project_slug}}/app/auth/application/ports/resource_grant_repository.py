import typing

from app.auth.domain.roles import ResourceGrant


class ResourceGrantRepository(typing.Protocol):
    async def exists(self, grant: ResourceGrant) -> bool: ...

    async def list_for_user(self, user_id: int) -> list[ResourceGrant]: ...

    async def add(self, grant: ResourceGrant) -> None:
        """Idempotent: adding an existing grant is a no-op."""
        ...

    async def delete(self, grant: ResourceGrant) -> None:
        """Idempotent: deleting a missing grant is a no-op."""
        ...

    async def delete_for_user(self, user_id: int) -> None: ...
