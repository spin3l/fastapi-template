import dataclasses

from app.{{ cookiecutter.module_name }}.application.ports.{{ cookiecutter.entity_name }}_repository import {{ cookiecutter.__entity_class }}Repository
from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import {{ cookiecutter.__entity_class }}, {{ cookiecutter.__entity_class }}Page


@dataclasses.dataclass(frozen=True, slots=True)
class {{ cookiecutter.__entity_class }}Service:
    repository: {{ cookiecutter.__entity_class }}Repository

    async def list_{{ cookiecutter.module_name }}(self) -> {{ cookiecutter.__entity_class }}Page:
        return {{ cookiecutter.__entity_class }}Page(results=await self.repository.list())

    async def get_{{ cookiecutter.entity_name }}(self, name: str) -> {{ cookiecutter.__entity_class }} | None:
        return await self.repository.get(name)
