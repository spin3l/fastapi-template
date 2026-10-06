import dataclasses

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.features.domain.constants import Features
from app.features.infrastructure.http.dependencies import require_feature
from app.grades.infrastructure.http.dependencies import GradingServiceDep
from app.grades.infrastructure.http.schemas import GradeResponse, GradesPageResponse

router = APIRouter(
    prefix="/grades",
    tags=["Grades"],
    dependencies=[Depends(require_feature(Features.GRADES))],
)


@router.get("/", response_model=GradesPageResponse)
@inject
async def list_grades(
    grading_service: GradingServiceDep,
) -> GradesPageResponse:
    page = await grading_service.get_grades()
    return GradesPageResponse.model_validate(dataclasses.asdict(page))


@router.get("/{subject}", response_model=GradeResponse)
@inject
async def get_grade(
    subject: str,
    grading_service: GradingServiceDep,
) -> GradeResponse:
    grade = await grading_service.get_grade(subject)
    if grade is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No grade for '{subject}'")

    return GradeResponse.model_validate(dataclasses.asdict(grade))
