"""Bootstrap admins: `make admin email=ada@example.com` (the user must have signed up first)."""

import argparse
import asyncio
import sys

from app.auth.domain.exceptions import UserNotFoundError
from app.di import Container


async def make_admin(email: str) -> int:
    container = Container()
    try:
        authorization = await container.authorization_service.async_()
        user = await authorization.promote_to_admin(email)
    except UserNotFoundError:
        print(f"No user with email {email!r}; sign up first.", file=sys.stderr)
        return 1
    finally:
        if (shutdown := container.shutdown_resources()) is not None:
            await shutdown

    print(f"{user.email} is now an admin.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.auth.infrastructure.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    make_admin_parser = commands.add_parser("make-admin", help="Give a user the admin role")
    make_admin_parser.add_argument("email")

    args = parser.parse_args()
    sys.exit(asyncio.run(make_admin(args.email)))


if __name__ == "__main__":
    main()
