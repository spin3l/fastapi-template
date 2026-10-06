import typing

from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import {{ cookiecutter.__entity_class }}


class {{ cookiecutter.__entity_class }}Repository(typing.Protocol):
    async def list(self) -> list[{{ cookiecutter.__entity_class }}]: ...

    async def get(self, name: str) -> {{ cookiecutter.__entity_class }} | None: ...
