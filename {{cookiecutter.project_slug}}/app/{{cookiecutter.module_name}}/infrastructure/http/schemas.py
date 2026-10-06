from app.shared.http.schemas import BaseSchema


class {{ cookiecutter.__entity_class }}Response(BaseSchema):
    name: str
    value: int


class {{ cookiecutter.__entity_class }}PageResponse(BaseSchema):
    results: list[{{ cookiecutter.__entity_class }}Response]
