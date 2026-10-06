import typing

from dependency_injector.wiring import Provide
from fastapi import Depends

from app.di import Container
from app.grades.application.service import GradingService

GradingServiceDep = typing.Annotated[GradingService, Depends(Provide[Container.grading_service])]
