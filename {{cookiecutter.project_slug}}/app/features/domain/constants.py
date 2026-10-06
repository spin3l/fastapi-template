import enum


class Features(enum.StrEnum):
    {{ cookiecutter.module_name.upper() }} = "is{{ cookiecutter.__module_class }}Enabled"
