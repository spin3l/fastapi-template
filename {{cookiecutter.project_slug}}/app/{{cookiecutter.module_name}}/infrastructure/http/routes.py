import dataclasses

from dependency_injector.wiring import inject
from fastapi import APIRouter, Depends

from app.auth.infrastructure.http.dependencies import require_resource_access
from app.features.domain.constants import Features
from app.features.infrastructure.http.dependencies import require_feature

# Sorted separately so the import order doesn't depend on the module name.
# isort: split
from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import RESOURCE_TYPE
from app.{{ cookiecutter.module_name }}.infrastructure.http.dependencies import {{ cookiecutter.__entity_class }}ServiceDep
from app.{{ cookiecutter.module_name }}.infrastructure.http.schemas import (
    {{ cookiecutter.__entity_class }}PageResponse,
    {{ cookiecutter.__entity_class }}Response,
    {{ cookiecutter.__entity_class }}UpdateRequest,
)

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
    return {{ cookiecutter.__entity_class }}Response.model_validate(dataclasses.asdict({{ cookiecutter.entity_name }}))


@router.put(
    "/{name}",
    response_model={{ cookiecutter.__entity_class }}Response,
    # Admins, or user admins granted this {{ cookiecutter.entity_name }} (`POST /users/{id}/grants`).
    dependencies=[Depends(require_resource_access(RESOURCE_TYPE, "name"))],
)
@inject
async def update_{{ cookiecutter.entity_name }}(
    name: str,
    body: {{ cookiecutter.__entity_class }}UpdateRequest,
    {{ cookiecutter.entity_name }}_service: {{ cookiecutter.__entity_class }}ServiceDep,
) -> {{ cookiecutter.__entity_class }}Response:
    {{ cookiecutter.entity_name }} = await {{ cookiecutter.entity_name }}_service.update_{{ cookiecutter.entity_name }}(name, body.value)
    return {{ cookiecutter.__entity_class }}Response.model_validate(dataclasses.asdict({{ cookiecutter.entity_name }}))
