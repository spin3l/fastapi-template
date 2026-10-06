# Feature Flags

FastAPI service exploring feature flags (ConfigCat) on top of a hexagonal architecture.

## Setup

```sh
cp .env.example .env   # fill in CONFIGCAT_SDK, JWT_SECRET, GOOGLE_*
uv sync
make hooks             # install the git pre-commit hook
make db                # Postgres in Docker on :5432
make migrate
make dev               # http://localhost:8000/docs
```

Or run everything in Docker with `make up` (Postgres → migrations → API on :8000), and stop it with `make down`.

## Auth

- `POST /auth/register`: create a user with email + password
- `POST /auth/login`: OAuth2 password form (`username` = email), returns a JWT bearer token
- `GET /auth/me`: current user (send `Authorization: Bearer <token>`)
- `GET /auth/google/login` → Google consent screen → `GET /auth/google/callback`, which returns a JWT

To enable Google sign-in, create an **OAuth client ID** (type *Web application*) in
Google Cloud Console → APIs & Services → Credentials. Add
`http://localhost:8000/auth/google/callback` as an authorized redirect URI, then set
`GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`.

Protect any route with `CurrentUserDep` from `app/auth/infrastructure/http/dependencies.py`.

## Commands

| Command          | What it does                                  |
| ---------------- | --------------------------------------------- |
| `make dev`       | Run the API with reload                       |
| `make test`      | Run the test suite                            |
| `make lint`      | Ruff + import-linter (layer contracts)        |
| `make typecheck` | mypy (strict)                                 |
| `make check`     | All of the above                              |
| `make hooks`     | Install the pre-commit git hook               |
| `make pre-commit`| Run every pre-commit hook on all files        |
| `make migrate`   | Apply Alembic migrations                      |
| `make migration m="message"` | Autogenerate a new migration      |
| `make db`        | Start only Postgres (docker compose)          |
| `make up` / `make down` | Start / stop the full Docker stack     |

## Layout

Each feature module (`auth`, `features`, `grades`) is split into three layers.
Dependencies only point inwards, and `make lint` enforces it.

```
<module>/
  domain/            # entities, value objects, domain errors (no frameworks)
  application/
    ports/           # interfaces the core needs (repositories, providers)
    service.py       # use cases
  infrastructure/
    http/            # driving adapter: routes, request/response schemas, FastAPI deps
    persistence/     # driven adapters: in-memory, SQLAlchemy, ...
```

- `app/di.py` is the composition root, the only place that picks which adapter goes behind each port.
- `app/main.py` builds the FastAPI app (`create_app` factory).
- `app/shared/` holds cross-cutting infrastructure: settings, logging, DB base and session, base HTTP schema.
