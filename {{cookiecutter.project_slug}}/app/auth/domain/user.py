import dataclasses

from app.auth.domain.exceptions import InactiveUserError


@dataclasses.dataclass(slots=True)
class User:
    email: str
    full_name: str
    hashed_password: str | None = None
    google_subject: str | None = None
    is_active: bool = True
    is_superuser: bool = False
    id: int | None = None

    def ensure_can_login(self) -> None:
        if not self.is_active:
            raise InactiveUserError()

    def link_google_account(self, subject: str) -> None:
        self.google_subject = subject


def normalize_email(email: str) -> str:
    return email.strip().lower()
