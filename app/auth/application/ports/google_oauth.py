import dataclasses
import typing


@dataclasses.dataclass(frozen=True, slots=True)
class GoogleIdentity:
    subject: str
    email: str
    email_verified: bool
    full_name: str


class GoogleOAuthClient(typing.Protocol):
    def authorization_url(self, state: str) -> str: ...

    async def fetch_identity(self, code: str) -> GoogleIdentity:
        """Exchange an authorization code for a verified identity, or raise
        `IdentityProviderError`."""
        ...
