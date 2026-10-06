import typing

from app.grades.domain.grades import Grade


class GradesRepository(typing.Protocol):
    async def list(self) -> list[Grade]: ...

    async def get(self, subject: str) -> Grade | None: ...
