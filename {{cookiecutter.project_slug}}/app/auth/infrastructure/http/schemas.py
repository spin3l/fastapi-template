import pydantic

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


class TokenResponse(pydantic.BaseModel):
    # Plain snake_case on purpose: OAuth2 clients (and Swagger's "Authorize") expect
    # `access_token` / `token_type`, not the camelCase aliases from BaseSchema.
    access_token: str
    token_type: str = "bearer"
