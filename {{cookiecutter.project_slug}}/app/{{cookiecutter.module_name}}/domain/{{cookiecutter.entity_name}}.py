import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class {{ cookiecutter.__entity_class }}:
    name: str
    value: int


@dataclasses.dataclass(frozen=True, slots=True)
class {{ cookiecutter.__entity_class }}Page:
    results: list[{{ cookiecutter.__entity_class }}]
