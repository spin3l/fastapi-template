from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.auth.domain.roles import ResourceGrant, Role
from app.auth.domain.user import User
from app.shared.db import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(64),
    )

    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
    )

    google_subject: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
    )

    is_active: Mapped[bool] = mapped_column(
        default=True,
    )

    # Plain string (not a native enum) so adding a role doesn't need an ALTER TYPE migration.
    role: Mapped[str] = mapped_column(
        String(20),
        default=Role.USER,
        server_default=Role.USER,
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            google_subject=self.google_subject,
            is_active=self.is_active,
            role=Role(self.role),
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserModel":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=user.hashed_password,
            google_subject=user.google_subject,
            is_active=user.is_active,
            role=user.role,
        )


class ResourceGrantModel(Base):
    __tablename__ = "resource_grants"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    resource_type: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    resource_id: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
    )

    def to_domain(self) -> ResourceGrant:
        return ResourceGrant(
            user_id=self.user_id,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
        )

    @classmethod
    def from_domain(cls, grant: ResourceGrant) -> "ResourceGrantModel":
        return cls(
            user_id=grant.user_id,
            resource_type=grant.resource_type,
            resource_id=grant.resource_id,
        )
