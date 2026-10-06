"""Create a local .env with a fresh JWT secret and print next steps."""

import pathlib
import secrets

example = pathlib.Path(".env.example")
env = pathlib.Path(".env")

if not env.exists():
    lines = [
        f"JWT_SECRET={secrets.token_hex(32)}" if line.startswith("JWT_SECRET=") else line
        for line in example.read_text().splitlines()
    ]
    env.write_text("\n".join(lines) + "\n")

print(
    """
Created {{ cookiecutter.project_slug }}/ (.env generated with a random JWT_SECRET).

Next steps:
  cd {{ cookiecutter.project_slug }}
  git init && uv sync && make hooks
  # set CONFIGCAT_SDK and GOOGLE_* in .env
  make db && make migrate && make dev     # http://localhost:8000/docs
"""
)
