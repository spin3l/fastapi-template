# FastAPI Hexagonal Template (cookiecutter)

This repo is a **cookiecutter template**. The generated project lives in
`{{cookiecutter.project_slug}}/`, and its own `CLAUDE.md` holds the architecture rules that apply
to code there. Follow those rules when editing template code.

## Editing template files

- Files under `{{cookiecutter.project_slug}}/` are Jinja templates. Use the variables from
  `cookiecutter.json` instead of hard-coded names:
  - `{{ cookiecutter.project_name }}` / `project_slug` / `__project_snake` (DB name, logger name)
  - `{{ cookiecutter.module_name }}` (plural snake_case) / `entity_name` (singular snake_case)
  - `{{ cookiecutter.__entity_class }}` / `__module_class` / `__module_title` / `__entity_label`
- File and directory names can use variables too (e.g. `app/{{cookiecutter.module_name}}/`).
- Literal `{{`, `{%` or `{#` in a template file must be escaped with `{% raw %}`, or the file
  must be listed in `_copy_without_render`.
- Rendered Python must be **ruff-format stable for any name length**. Prefer explicit multi-line
  calls with a trailing comma over lines whose wrapping depends on how long a name is.
- `uv.lock` is templated (project name only). After changing dependencies, regenerate a project,
  run `uv lock` there, and copy the lockfile back with the `{{ cookiecutter.project_slug }}` name
  restored.

## Verifying

Always run `make test-template` after a change. It renders the template with several answer sets
(defaults, `Feature Flags`/`grades`, multi-word names), checks that no Jinja is left unrendered, and
runs `uv lock --check`, `ruff format --check` and `make check` in each generated project. Output goes
to `.generated/` (gitignored).
