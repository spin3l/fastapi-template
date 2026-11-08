import dataclasses

# Name used in `ResourceGrant.resource_type` to grant user admins access to one {{ cookiecutter.entity_name }}.
RESOURCE_TYPE = "{{ cookiecutter.entity_name }}"


@dataclasses.dataclass(frozen=True, slots=True)
class {{ cookiecutter.__entity_class }}:
    name: str
    value: int


@dataclasses.dataclass(frozen=True, slots=True)
class {{ cookiecutter.__entity_class }}Page:
    results: list[{{ cookiecutter.__entity_class }}]
