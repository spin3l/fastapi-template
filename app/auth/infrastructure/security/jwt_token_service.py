import dataclasses
import datetime
import typing

import jwt
import pydantic

from app.auth.application.ports.token_service import TokenService
from app.auth.domain.exceptions import InvalidTokenError


@dataclasses.dataclass(frozen=True, slots=True)
class JwtTokenService(TokenService):
    secret: pydantic.SecretStr
    algorithm: str
    ttl_minutes: int
    issuer: str = "feature-flags"

    @typing.override
    def issue(self, user_id: int) -> str:
        now = datetime.datetime.now(datetime.UTC)
        claims = {
            "sub": str(user_id),
            "iss": self.issuer,
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self.ttl_minutes),
        }
        return jwt.encode(claims, self.secret.get_secret_value(), algorithm=self.algorithm)

    @typing.override
    def verify(self, token: str) -> int:
        try:
            claims = jwt.decode(
                token,
                self.secret.get_secret_value(),
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={"require": ["sub", "iss", "iat", "exp"]},
            )
            return int(claims["sub"])
        except (jwt.PyJWTError, ValueError) as exc:
            raise InvalidTokenError() from exc
