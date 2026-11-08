import collections.abc
import typing

from dependency_injector.wiring import Provide, inject
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.auth.application.authorization_service import AuthorizationService
from app.auth.application.service import AuthService
from app.auth.domain.user import User
from app.di import Container

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

AuthServiceDep = typing.Annotated[AuthService, Depends(Provide[Container.auth_service])]
AuthorizationServiceDep = typing.Annotated[
    AuthorizationService,
    Depends(Provide[Container.authorization_service]),
]


@inject
async def get_current_user(
    token: typing.Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    return await auth_service.authenticate(token)


CurrentUserDep = typing.Annotated[User, Depends(get_current_user)]


@inject
async def get_authorization_service(
    authorization_service: AuthorizationServiceDep,
) -> AuthorizationService:
    return authorization_service


async def get_admin_user(user: CurrentUserDep) -> User:
    user.ensure_admin()
    return user


AdminUserDep = typing.Annotated[User, Depends(get_admin_user)]


def require_resource_access(
    resource_type: str,
    path_param: str,
) -> collections.abc.Callable[..., typing.Awaitable[User]]:
    """Admins pass; user admins pass only with a grant for the resource named in `path_param`.

    `@router.put("/{name}", dependencies=[Depends(require_resource_access("book", "name"))])`
    """

    async def dependency(
        request: Request,
        user: CurrentUserDep,
        authorization: typing.Annotated[
            AuthorizationService,
            Depends(get_authorization_service),
        ],
    ) -> User:
        resource_id = str(request.path_params[path_param])
        await authorization.ensure_can_manage(user, resource_type, resource_id)
        return user

    return dependency
