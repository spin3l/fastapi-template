import typing

from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.auth.application.service import AuthService
from app.auth.domain.user import User
from app.di import Container

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

AuthServiceDep = typing.Annotated[AuthService, Depends(Provide[Container.auth_service])]


@inject
async def get_current_user(
    token: typing.Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthServiceDep,
) -> User:
    return await auth_service.authenticate(token)


CurrentUserDep = typing.Annotated[User, Depends(get_current_user)]
