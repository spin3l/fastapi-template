import pytest

from app.grades.application.service import GradingService
from app.grades.domain.grades import Grade, GradePage
from app.grades.infrastructure.persistence.in_memory import InMemoryGradesRepository


@pytest.mark.anyio
async def test_get_grades_returns_page_from_repository() -> None:
    grades = {"Physics": Grade(subject="Physics", value=9)}
    service = GradingService(repository=InMemoryGradesRepository(grades=grades))

    assert await service.get_grades() == GradePage(results=[Grade(subject="Physics", value=9)])


@pytest.mark.anyio
async def test_get_grade_returns_none_when_missing() -> None:
    service = GradingService(repository=InMemoryGradesRepository(grades={}))

    assert await service.get_grade("Physics") is None
