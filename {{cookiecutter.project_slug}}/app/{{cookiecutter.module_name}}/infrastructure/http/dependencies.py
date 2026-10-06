import typing

from dependency_injector.wiring import Provide
from fastapi import Depends

from app.di import Container
from app.{{ cookiecutter.module_name }}.application.service import {{ cookiecutter.__entity_class }}Service

{{ cookiecutter.__entity_class }}ServiceDep = typing.Annotated[
    {{ cookiecutter.__entity_class }}Service,
    Depends(Provide[Container.{{ cookiecutter.entity_name }}_service]),
]
