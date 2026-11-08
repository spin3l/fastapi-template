class {{ cookiecutter.__entity_class }}Error(Exception):
    message = "{{ cookiecutter.__entity_label }} error"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.message)


class {{ cookiecutter.__entity_class }}NotFoundError({{ cookiecutter.__entity_class }}Error):
    def __init__(self, name: str) -> None:
        super().__init__(f"No {{ cookiecutter.__entity_label }} for '{name}'")
        self.name = name
