import typing


class PasswordHasher(typing.Protocol):
    async def hash(self, password: str) -> str: ...

    async def verify(self, password: str, hashed_password: str) -> bool: ...
