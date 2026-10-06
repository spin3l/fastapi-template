# FastAPI Hexagonal Template

[Cookiecutter](https://cookiecutter.readthedocs.io) template for FastAPI services built on a
hexagonal (ports and adapters) architecture.

## What you get

- **FastAPI** app factory with structured logging (structlog) and correlation IDs
- **Hexagonal layout** per module (`domain` / `application` / `infrastructure`), enforced by
  import-linter
- **Auth module**: email + password (Argon2) and Google OAuth sign-in, issuing JWTs (pyjwt)
- **Feature flags** via ConfigCat, with route-level gating
- **An example domain module** named from your answers (entity, repository port, in-memory adapter,
  service, routes, tests)
- **PostgreSQL** with async SQLAlchemy and Alembic migrations
- **dependency-injector** container as the single composition root
- **Docker**: multi-stage uv Dockerfile, and compose with Postgres → migrations → API
- **Quality gates**: ruff, mypy (strict), import-linter, pytest, and pre-commit running all of them
- **Claude Code setup**: `CLAUDE.md` with the architecture rules, plus a hook that checks layer
  contracts after every edit

## Usage

```sh
uvx cookiecutter gh:<you>/<this-repo>      # or: uvx cookiecutter /path/to/this/repo
```

| Prompt                | Example        | Used for                                        |
| --------------------- | -------------- | ----------------------------------------------- |
| `project_name`        | `Order Hub`    | API title, README, CLAUDE.md                    |
| `project_slug`        | `order-hub`    | package name, compose project, image, JWT issuer |
| `project_description` |                | pyproject, README                               |
| `module_name`         | `orders`       | example module package, route prefix, feature flag |
| `entity_name`         | `order`        | entity/repository/service class names (`Order`, `OrderRepository`, ...) |

The slug, the snake_case DB name and the class names are derived from these. A post-generation hook
writes `.env` with a random `JWT_SECRET` and prints the next steps.

## Developing the template

```sh
uv sync            # cookiecutter + pre-commit
make hooks         # install this repo's pre-commit hook
make test-template # render with several answer sets, run each project's `make check`
make generate      # interactive generation into ../
```

The project lives in `{{cookiecutter.project_slug}}/`. Its files contain Jinja, so linters can't run
on them directly. `make test-template` is the source of truth, and the pre-commit hook runs it
whenever template files change.
