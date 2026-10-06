import dataclasses

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends, HTTPException, status

from app.features.domain.constants import Features
from app.features.infrastructure.http.dependencies import require_feature
from app.{{ cookiecutter.module_name }}.infrastructure.http.dependencies import {{ cookiecutter.__entity_class }}ServiceDep
from app.{{ cookiecutter.module_name }}.infrastructure.http.schemas import {{ cookiecutter.__entity_class }}PageResponse, {{ cookiecutter.__entity_class }}Response

router = APIRouter(
    prefix="/{{ cookiecutter.module_name }}",
    tags=["{{ cookiecutter.__module_title }}"],
    dependencies=[Depends(require_feature(Features.{{ cookiecutter.module_name.upper() }}))],
)


@router.get("/", response_model={{ cookiecutter.__entity_class }}PageResponse)
@inject
async def list_{{ cookiecutter.module_name }}(
    {{ cookiecutter.entity_name }}_service: {{ cookiecutter.__entity_class }}ServiceDep,
) -> {{ cookiecutter.__entity_class }}PageResponse:
    page = await {{ cookiecutter.entity_name }}_service.list_{{ cookiecutter.module_name }}()
    return {{ cookiecutter.__entity_class }}PageResponse.model_validate(dataclasses.asdict(page))


@router.get("/{name}", response_model={{ cookiecutter.__entity_class }}Response)
@inject
async def get_{{ cookiecutter.entity_name }}(
    name: str,
    {{ cookiecutter.entity_name }}_service: {{ cookiecutter.__entity_class }}ServiceDep,
) -> {{ cookiecutter.__entity_class }}Response:
    {{ cookiecutter.entity_name }} = await {{ cookiecutter.entity_name }}_service.get_{{ cookiecutter.entity_name }}(name)
    if {{ cookiecutter.entity_name }} is None:
        detail = f"No {{ cookiecutter.__entity_label }} for '{name}'"
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail)

    return {{ cookiecutter.__entity_class }}Response.model_validate(dataclasses.asdict({{ cookiecutter.entity_name }}))
