import pydantic

from app.auth.domain.roles import Role
from app.shared.http.schemas import BaseSchema


class UserCreateRequest(BaseSchema):
    email: pydantic.EmailStr
    full_name: str = pydantic.Field(min_length=1, max_length=64)
    password: str = pydantic.Field(min_length=8, max_length=128)


class UserResponse(BaseSchema):
    id: int
    email: str
    full_name: str
    is_active: bool
    role: Role


class RoleUpdateRequest(BaseSchema):
    role: Role


class ResourceGrantRequest(BaseSchema):
    resource_type: str = pydantic.Field(min_length=1, max_length=64)
    resource_id: str = pydantic.Field(min_length=1, max_length=255)


class ResourceGrantResponse(BaseSchema):
    resource_type: str
    resource_id: str


class TokenResponse(pydantic.BaseModel):
    # Plain snake_case on purpose: OAuth2 clients (and Swagger's "Authorize") expect
    # `access_token` / `token_type`, not the camelCase aliases from BaseSchema.
    access_token: str
    token_type: str = "bearer"
