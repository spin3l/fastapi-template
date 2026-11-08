import pytest

from app.auth.application.authorization_service import AuthorizationService
from app.auth.domain.exceptions import (
    CannotChangeOwnRoleError,
    ForbiddenError,
    InvalidGrantError,
    UserNotFoundError,
)
from app.auth.domain.roles import ResourceGrant, Role
from app.auth.domain.user import User
from tests.fakes import InMemoryResourceGrantRepository, InMemoryUserRepository

pytestmark = pytest.mark.anyio


async def _user(users: InMemoryUserRepository, name: str, role: Role = Role.USER) -> User:
    return await users.add(User(email=f"{name}@example.com", full_name=name, role=role))


def _grant(user: User, resource_id: str = "42") -> ResourceGrant:
    assert user.id is not None
    return ResourceGrant(user_id=user.id, resource_type="book", resource_id=resource_id)


async def test_admin_can_manage_any_resource(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    admin = await _user(users, "admin", Role.ADMIN)

    await authorization_service.ensure_can_manage(admin, "book", "42")


async def test_user_admin_can_manage_only_granted_resources(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
    grants: InMemoryResourceGrantRepository,
) -> None:
    user_admin = await _user(users, "ua", Role.USER_ADMIN)
    await grants.add(_grant(user_admin, "42"))

    await authorization_service.ensure_can_manage(user_admin, "book", "42")
    with pytest.raises(ForbiddenError):
        await authorization_service.ensure_can_manage(user_admin, "book", "43")
    with pytest.raises(ForbiddenError):
        await authorization_service.ensure_can_manage(user_admin, "other", "42")


async def test_user_cannot_manage_even_with_a_stray_grant(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
    grants: InMemoryResourceGrantRepository,
) -> None:
    user = await _user(users, "ada")
    await grants.add(_grant(user))

    with pytest.raises(ForbiddenError):
        await authorization_service.ensure_can_manage(user, "book", "42")


@pytest.mark.parametrize("actor_role", [Role.USER, Role.USER_ADMIN])
async def test_only_admins_change_roles_and_grants(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
    actor_role: Role,
) -> None:
    actor = await _user(users, "actor", actor_role)
    target = await _user(users, "target", Role.USER_ADMIN)
    assert target.id is not None

    with pytest.raises(ForbiddenError):
        await authorization_service.set_role(actor, target.id, Role.ADMIN)
    with pytest.raises(ForbiddenError):
        await authorization_service.grant(actor, _grant(target))
    with pytest.raises(ForbiddenError):
        await authorization_service.list_grants(actor, target.id)


async def test_admin_cannot_change_own_role(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    admin = await _user(users, "admin", Role.ADMIN)
    assert admin.id is not None

    with pytest.raises(CannotChangeOwnRoleError):
        await authorization_service.set_role(admin, admin.id, Role.USER)


async def test_set_role_on_missing_user(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    admin = await _user(users, "admin", Role.ADMIN)

    with pytest.raises(UserNotFoundError):
        await authorization_service.set_role(admin, 999, Role.USER_ADMIN)


async def test_grants_require_user_admin_role(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    admin = await _user(users, "admin", Role.ADMIN)
    user = await _user(users, "ada")

    with pytest.raises(InvalidGrantError):
        await authorization_service.grant(admin, _grant(user))


async def test_demoting_user_admin_drops_their_grants(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    admin = await _user(users, "admin", Role.ADMIN)
    user_admin = await _user(users, "ua", Role.USER_ADMIN)
    assert user_admin.id is not None
    await authorization_service.grant(admin, _grant(user_admin))

    await authorization_service.set_role(admin, user_admin.id, Role.USER)
    await authorization_service.set_role(admin, user_admin.id, Role.USER_ADMIN)

    assert await authorization_service.list_grants(admin, user_admin.id) == []


async def test_promote_to_admin_by_email(
    authorization_service: AuthorizationService,
    users: InMemoryUserRepository,
) -> None:
    await _user(users, "ada")

    user = await authorization_service.promote_to_admin(" ADA@example.com ")

    assert user.role is Role.ADMIN


async def test_promote_to_admin_unknown_email(
    authorization_service: AuthorizationService,
) -> None:
    with pytest.raises(UserNotFoundError):
        await authorization_service.promote_to_admin("nobody@example.com")
