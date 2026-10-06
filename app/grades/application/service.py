import dataclasses

from app.grades.application.ports.grades_repository import GradesRepository
from app.grades.domain.grades import Grade, GradePage


@dataclasses.dataclass(frozen=True, slots=True)
class GradingService:
    repository: GradesRepository

    async def get_grades(self) -> GradePage:
        return GradePage(results=await self.repository.list())

    async def get_grade(self, subject: str) -> Grade | None:
        return await self.repository.get(subject)
