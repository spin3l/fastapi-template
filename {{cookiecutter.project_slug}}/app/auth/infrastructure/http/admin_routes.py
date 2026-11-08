from dependency_injector.wiring import inject
from fastapi import APIRouter, status

from app.auth.domain.roles import ResourceGrant
from app.auth.infrastructure.http.dependencies import AuthorizationServiceDep, CurrentUserDep
from app.auth.infrastructure.http.schemas import (
    ResourceGrantRequest,
    ResourceGrantResponse,
    RoleUpdateRequest,
    UserResponse,
)

# Admin-only: `AuthorizationService` checks the actor's role on every call.
router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.patch("/{user_id}/role", response_model=UserResponse)
@inject
async def set_role(
    user_id: int,
    body: RoleUpdateRequest,
    actor: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> UserResponse:
    user = await authorization.set_role(actor, user_id, body.role)
    return UserResponse.model_validate(user, from_attributes=True)


@router.get("/{user_id}/grants", response_model=list[ResourceGrantResponse])
@inject
async def list_grants(
    user_id: int,
    actor: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> list[ResourceGrantResponse]:
    grants = await authorization.list_grants(actor, user_id)
    return [ResourceGrantResponse.model_validate(g, from_attributes=True) for g in grants]


@router.post(
    "/{user_id}/grants",
    response_model=ResourceGrantResponse,
    status_code=status.HTTP_201_CREATED,
)
@inject
async def add_grant(
    user_id: int,
    body: ResourceGrantRequest,
    actor: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> ResourceGrantResponse:
    grant = await authorization.grant(
        actor,
        ResourceGrant(
            user_id=user_id,
            resource_type=body.resource_type,
            resource_id=body.resource_id,
        ),
    )
    return ResourceGrantResponse.model_validate(grant, from_attributes=True)


@router.delete(
    "/{user_id}/grants/{resource_type}/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
@inject
async def revoke_grant(
    user_id: int,
    resource_type: str,
    resource_id: str,
    actor: CurrentUserDep,
    authorization: AuthorizationServiceDep,
) -> None:
    await authorization.revoke(
        actor,
        ResourceGrant(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
        ),
    )
