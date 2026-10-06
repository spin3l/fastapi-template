import pytest

from app.{{ cookiecutter.module_name }}.application.service import {{ cookiecutter.__entity_class }}Service
from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import {{ cookiecutter.__entity_class }}, {{ cookiecutter.__entity_class }}Page
from app.{{ cookiecutter.module_name }}.infrastructure.persistence.in_memory import InMemory{{ cookiecutter.__entity_class }}Repository


@pytest.mark.anyio
async def test_list_{{ cookiecutter.module_name }}_returns_page_from_repository() -> None:
    {{ cookiecutter.module_name }} = {"other": {{ cookiecutter.__entity_class }}(name="other", value=9)}
    service = {{ cookiecutter.__entity_class }}Service(repository=InMemory{{ cookiecutter.__entity_class }}Repository({{ cookiecutter.module_name }}={{ cookiecutter.module_name }}))

    assert await service.list_{{ cookiecutter.module_name }}() == {{ cookiecutter.__entity_class }}Page(
        results=[{{ cookiecutter.__entity_class }}(name="other", value=9)],
    )


@pytest.mark.anyio
async def test_get_{{ cookiecutter.entity_name }}_returns_none_when_missing() -> None:
    service = {{ cookiecutter.__entity_class }}Service(repository=InMemory{{ cookiecutter.__entity_class }}Repository({{ cookiecutter.module_name }}={}))

    assert await service.get_{{ cookiecutter.entity_name }}("missing") is None
