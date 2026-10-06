"""Validate cookiecutter answers before anything is rendered."""

import keyword
import re
import sys

PROJECT_NAME = "{{ cookiecutter.project_name }}"
PROJECT_SLUG = "{{ cookiecutter.project_slug }}"
MODULE_NAME = "{{ cookiecutter.module_name }}"
ENTITY_NAME = "{{ cookiecutter.entity_name }}"

# Module names already used by the template, plus names that would shadow imports.
RESERVED = {"app", "alembic", "auth", "features", "shared", "tests", "di", "main"}
IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")

errors = []

if not PROJECT_NAME.strip() or re.search(r"[\"'\\]", PROJECT_NAME):
    errors.append("project_name must be non-empty and contain no quotes or backslashes.")

if not re.fullmatch(r"[a-z][a-z0-9-]*", PROJECT_SLUG):
    errors.append(f"project_slug {PROJECT_SLUG!r} must be lowercase letters, digits and dashes.")

for label, value in (("module_name", MODULE_NAME), ("entity_name", ENTITY_NAME)):
    if not IDENTIFIER.fullmatch(value):
        errors.append(f"{label} {value!r} must be snake_case (a-z, 0-9, _), starting with a letter.")
    elif keyword.iskeyword(value) or value in RESERVED:
        errors.append(f"{label} {value!r} is reserved; pick another name.")

if errors:
    print("\n".join(f"ERROR: {e}" for e in errors), file=sys.stderr)
    sys.exit(1)
