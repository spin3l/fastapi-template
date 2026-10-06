import secrets
import typing

from dependency_injector.wiring import inject
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.infrastructure.http.dependencies import AuthServiceDep, CurrentUserDep
from app.auth.infrastructure.http.schemas import TokenResponse, UserCreateRequest, UserResponse

GOOGLE_STATE_COOKIE = "google_oauth_state"

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@inject
async def register(
    user_dto: UserCreateRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    user = await auth_service.register(
        email=user_dto.email,
        full_name=user_dto.full_name,
        password=user_dto.password,
    )
    return UserResponse.model_validate(user, from_attributes=True)


@router.post("/login", response_model=TokenResponse)
@inject
async def login(
    form: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    token = await auth_service.login(email=form.username, password=form.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(user, from_attributes=True)


@router.get("/google/login")
@inject
async def google_login(
    request: Request,
    auth_service: AuthServiceDep,
) -> RedirectResponse:
    # Random `state` bound to this browser via a cookie protects the callback from CSRF.
    state = secrets.token_urlsafe(32)

    response = RedirectResponse(auth_service.google_authorization_url(state))
    response.set_cookie(
        GOOGLE_STATE_COOKIE,
        state,
        max_age=600,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https",
    )
    return response


@router.get("/google/callback", response_model=TokenResponse)
@inject
async def google_callback(
    code: str,
    state: str,
    response: Response,
    auth_service: AuthServiceDep,
    expected_state: typing.Annotated[str | None, Cookie(alias=GOOGLE_STATE_COOKIE)] = None,
) -> TokenResponse:
    if expected_state is None or not secrets.compare_digest(state, expected_state):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid OAuth state")

    response.delete_cookie(GOOGLE_STATE_COOKIE)

    token = await auth_service.login_with_google(code)
    return TokenResponse(access_token=token)
