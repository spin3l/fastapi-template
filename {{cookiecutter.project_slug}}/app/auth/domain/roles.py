import dataclasses
import enum


class Role(enum.StrEnum):
    USER = "user"
    # Manages only the resources granted to them (see `ResourceGrant`).
    USER_ADMIN = "user_admin"
    # Manages everything, including roles and grants.
    ADMIN = "admin"


@dataclasses.dataclass(frozen=True, slots=True)
class ResourceGrant:
    """Lets a `USER_ADMIN` manage one resource, e.g. `("order_item", "42")`."""

    user_id: int
    resource_type: str
    resource_id: str
