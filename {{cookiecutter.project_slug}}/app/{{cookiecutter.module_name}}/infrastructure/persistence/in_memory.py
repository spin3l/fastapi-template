import dataclasses
import typing

from app.{{ cookiecutter.module_name }}.application.ports.{{ cookiecutter.entity_name }}_repository import {{ cookiecutter.__entity_class }}Repository
from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import {{ cookiecutter.__entity_class }}


@dataclasses.dataclass(frozen=True, slots=True)
class InMemory{{ cookiecutter.__entity_class }}Repository({{ cookiecutter.__entity_class }}Repository):
    {{ cookiecutter.module_name }}: dict[str, {{ cookiecutter.__entity_class }}] = dataclasses.field(
        default_factory=lambda: {"example": {{ cookiecutter.__entity_class }}(name="example", value=1)},
    )

    @typing.override
    async def list(self) -> list[{{ cookiecutter.__entity_class }}]:
        return list(self.{{ cookiecutter.module_name }}.values())

    @typing.override
    async def get(self, name: str) -> {{ cookiecutter.__entity_class }} | None:
        return self.{{ cookiecutter.module_name }}.get(name)
