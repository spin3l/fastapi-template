from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

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

    is_superuser: Mapped[bool] = mapped_column(
        default=False,
    )

    def to_domain(self) -> User:
        return User(
            id=self.id,
            email=self.email,
            full_name=self.full_name,
            hashed_password=self.hashed_password,
            google_subject=self.google_subject,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
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
            is_superuser=user.is_superuser,
        )
