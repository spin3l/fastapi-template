# {{ cookiecutter.project_name }}

FastAPI + SQLAlchemy (async) + dependency-injector, organized as a **hexagonal architecture**.
Python 3.13, managed with `uv`. Run `make check` (ruff + import-linter + mypy strict + pytest)
before considering a change done. A pre-commit hook (`.pre-commit-config.yaml`) runs the same
checks plus file hygiene on every commit. Fix failures instead of bypassing them with `--no-verify`.

## Layout

```
app/
  main.py            # create_app() factory: middleware, routers, exception handlers, wiring
  handlers.py        # registers shared + every module's exception handlers
  di.py              # composition root: the ONLY place that picks an adapter for a port
  shared/            # cross-cutting infra: config (Settings), logs, db (Base/engine), http/{schemas,errors,health}
  alembic/           # migrations (hand-written or `make migration m="..."`)
  <module>/          # auth, features, {{ cookiecutter.module_name }}, ...
    domain/          # entities (plain dataclasses), value objects, domain exceptions
    application/
      ports/         # typing.Protocol interfaces the core needs (repositories, providers, ...)
      service.py     # use cases; depend ONLY on ports + domain
    infrastructure/
      http/          # driving adapter: routes.py, schemas.py (pydantic), dependencies.py, errors.py
      persistence/   # driven adapters: SQLAlchemy repos, orm.py (UserModel + to/from_domain), in-memory
      <vendor>/      # other driven adapters (google/, security/, configcat.py, ...)
tests/
  fakes.py           # in-memory fakes implementing the ports
  conftest.py        # `client` fixture overrides container providers with fakes
```

## Rules (import-linter enforces the first two; a hook runs it after every edit)

- **Dependencies point inwards:** `infrastructure → application → domain`. Domain and application
  never import fastapi, sqlalchemy, httpx, jwt, pwdlib, configcatclient, dependency_injector or `app.di`.
- **No `__init__.py` files.** `app/` and `tests/` are PEP 420 namespace packages; mypy
  (`explicit_package_bases`), pytest (`pythonpath = ["."]`) and import-linter are configured for it.
- **Ports are `typing.Protocol`** with plain names (`UserRepository`, not `IUserRepository`).
  Adapters subclass the port explicitly and mark methods with `@typing.override`.
- **Domain objects are dataclasses, not ORM models or pydantic.** ORM models live in
  `infrastructure/persistence/orm.py` and convert with `to_domain()` / `from_domain()`.
- **HTTP schemas live in `infrastructure/http/schemas.py`** and extend `shared.http.schemas.BaseSchema`
  (camelCase aliases). Exception: OAuth2 token responses stay snake_case.
- **Routes never call driven ports directly**; they go through an application service.
- **Transactions:** a service runs each use case inside `async with self.uow() as uow:` (a
  `UnitOfWork` port, see `app/auth/application/ports/unit_of_work.py`), which commits on success and
  rolls back on error. Repositories receive the session, `flush()` but never commit, and turn
  unique-constraint `IntegrityError`s into domain exceptions. Keep slow work (hashing, HTTP calls)
  outside the `async with`.
- **Errors:** domain and application code raise domain exceptions (`domain/exceptions.py`); routes
  never raise `HTTPException`; each module's `http/errors.py` maps them to status
  codes in a `register_exception_handlers(app)` function, which is called from `app/handlers.py`.
  Build responses with `shared.http.errors.error_response` so every error body is
  `{"detail": ..., "code": ...}`. Unhandled exceptions are logged and returned as a generic 500.
- **Wiring a new adapter:** add a provider in `di.py` typed as the port
  (`providers.Singleton[Port]`). Use `providers.Resource` for anything that must be closed on
  shutdown (clients, engines). Add any module using `Provide[...]` to `container.wire(...)` in `main.py`.
- **Feature flags:** gate routers with `dependencies=[Depends(require_feature(Features.X))]`.
- **Auth:** protect routes with `CurrentUserDep` from `app/auth/infrastructure/http/dependencies.py`.
- **Roles:** `user` < `user_admin` (only resources granted via `resource_grants`) < `admin` (everything).
  Gate a route that changes one resource with
  `Depends(require_resource_access(RESOURCE_TYPE, "<path param>"))`, where `RESOURCE_TYPE` is a
  constant in the module's domain; gate admin-only routes with `AdminUserDep`. Role and grant
  rules live in `AuthorizationService`; services that take an `actor` check permissions themselves.
- **Blocking work** (hashing, sync SDKs) runs via `anyio.to_thread.run_sync`.
- **Probes:** `GET /health` is liveness (no dependencies); `GET /ready` checks the database.
- **Config** goes in `shared/config.py` `Settings`, plus a line in `.env.example`. Never commit `.env`.

## Testing

- Unit-test services with fakes from `tests/fakes.py`; API-test via the `client` fixture, which
  overrides container providers (no real DB, ConfigCat or Google).
- New ports need a fake in `tests/fakes.py`.

## Running

- `make dev`: local reload server (needs `make db` for Postgres)
- `make up` / `make down`: full stack in Docker (db → migrate → api on :8000)
- `make migrate`, `make migration m="..."`: Alembic
