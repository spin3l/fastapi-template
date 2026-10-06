# FastAPI Template

[Cookiecutter](https://cookiecutter.readthedocs.io) template for FastAPI services with a hexagonal
architecture: auth (password + Google OAuth, JWT), ConfigCat feature flags, async SQLAlchemy +
Alembic, Docker, and strict checks (ruff, mypy, import-linter, pytest) wired into pre-commit.

## Usage

```sh
uvx cookiecutter https://github.com/spin3l/fastapi-template
```

You'll be asked for a project name and an example domain module (e.g. `orders` / `order`), which
names the generated code. Then:

```sh
cd <project-slug>
git init && uv sync && make hooks
make db && make migrate && make dev   # http://localhost:8000/docs
```

## Developing the template

Run `make test-template` after changes. It generates sample projects and runs their full checks.
