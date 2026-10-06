import dataclasses
import typing

from app.grades.application.ports.grades_repository import GradesRepository
from app.grades.domain.grades import Grade


@dataclasses.dataclass(frozen=True, slots=True)
class InMemoryGradesRepository(GradesRepository):
    grades: dict[str, Grade] = dataclasses.field(
        default_factory=lambda: {"Maths": Grade(subject="Maths", value=11)},
    )

    @typing.override
    async def list(self) -> list[Grade]:
        return list(self.grades.values())

    @typing.override
    async def get(self, subject: str) -> Grade | None:
        return self.grades.get(subject)
