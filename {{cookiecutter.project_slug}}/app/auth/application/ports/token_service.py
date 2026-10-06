import typing


class TokenService(typing.Protocol):
    def issue(self, user_id: int) -> str: ...

    def verify(self, token: str) -> int:
        """Return the user id the token was issued for, or raise `InvalidTokenError`."""
        ...
