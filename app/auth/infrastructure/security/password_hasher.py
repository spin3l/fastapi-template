import dataclasses
import typing

import anyio.to_thread
from pwdlib import PasswordHash

from app.auth.application.ports.password_hasher import PasswordHasher


@dataclasses.dataclass(frozen=True, slots=True)
class PwdlibPasswordHasher(PasswordHasher):
    password_hash: PasswordHash = dataclasses.field(default_factory=PasswordHash.recommended)

    # Argon2 is deliberately slow; run it off the event loop.
    @typing.override
    async def hash(self, password: str) -> str:
        return await anyio.to_thread.run_sync(self.password_hash.hash, password)

    @typing.override
    async def verify(self, password: str, hashed_password: str) -> bool:
        return await anyio.to_thread.run_sync(self.password_hash.verify, password, hashed_password)
