import collections.abc
import dataclasses

from app.auth.application.ports.unit_of_work import UnitOfWork
from app.auth.domain.exceptions import (
    CannotChangeOwnRoleError,
    ForbiddenError,
    InvalidGrantError,
    UserNotFoundError,
)
from app.auth.domain.roles import ResourceGrant, Role
from app.auth.domain.user import User, normalize_email


@dataclasses.dataclass(frozen=True, slots=True)
class AuthorizationService:
    """Who may manage what. `actor` is always the authenticated user making the request."""

    uow: collections.abc.Callable[[], UnitOfWork]

    async def ensure_can_manage(self, actor: User, resource_type: str, resource_id: str) -> None:
        if actor.role is Role.ADMIN:
            return

        if actor.role is Role.USER_ADMIN and actor.id is not None:
            grant = ResourceGrant(
                user_id=actor.id,
                resource_type=resource_type,
                resource_id=resource_id,
            )
            async with self.uow() as uow:
                if await uow.grants.exists(grant):
                    return

        raise ForbiddenError()

    async def set_role(self, actor: User, user_id: int, role: Role) -> User:
        actor.ensure_admin()
        if actor.id == user_id:
            # Stops the last admin from locking everyone out.
            raise CannotChangeOwnRoleError()

        async with self.uow() as uow:
            user = await uow.users.get_by_id(user_id)
            if user is None:
                raise UserNotFoundError()

            return await self._apply_role(uow, user, role)

    async def promote_to_admin(self, email: str) -> User:
        """Bootstraps the first admin (used by the CLI, so there's no actor)."""
        async with self.uow() as uow:
            user = await uow.users.get_by_email(normalize_email(email))
            if user is None:
                raise UserNotFoundError()

            return await self._apply_role(uow, user, Role.ADMIN)

    async def list_grants(self, actor: User, user_id: int) -> list[ResourceGrant]:
        actor.ensure_admin()

        async with self.uow() as uow:
            if await uow.users.get_by_id(user_id) is None:
                raise UserNotFoundError()

            return await uow.grants.list_for_user(user_id)

    async def grant(self, actor: User, grant: ResourceGrant) -> ResourceGrant:
        actor.ensure_admin()

        async with self.uow() as uow:
            user = await uow.users.get_by_id(grant.user_id)
            if user is None:
                raise UserNotFoundError()
            if user.role is not Role.USER_ADMIN:
                raise InvalidGrantError()

            await uow.grants.add(grant)
            return grant

    async def revoke(self, actor: User, grant: ResourceGrant) -> None:
        actor.ensure_admin()

        async with self.uow() as uow:
            await uow.grants.delete(grant)

    async def _apply_role(self, uow: UnitOfWork, user: User, role: Role) -> User:
        assert user.id is not None
        if role is not Role.USER_ADMIN:
            # Grants only mean something for user admins; drop them so a later
            # re-promotion doesn't silently restore old access.
            await uow.grants.delete_for_user(user.id)

        user.role = role
        return await uow.users.update(user)
