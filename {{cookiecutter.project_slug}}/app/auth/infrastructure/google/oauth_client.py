import dataclasses
import typing
import urllib.parse

import anyio.to_thread
import httpx
import jwt
import pydantic

from app.auth.application.ports.google_oauth import GoogleIdentity, GoogleOAuthClient
from app.auth.domain.exceptions import IdentityProviderError

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
ISSUERS = ["https://accounts.google.com", "accounts.google.com"]


async def create_http_client() -> typing.AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=10) as client:
        yield client


@dataclasses.dataclass(frozen=True, slots=True)
class GoogleOAuthHttpClient(GoogleOAuthClient):
    http: httpx.AsyncClient
    client_id: str
    client_secret: pydantic.SecretStr
    redirect_uri: str
    jwks: jwt.PyJWKClient = dataclasses.field(default_factory=lambda: jwt.PyJWKClient(JWKS_URL))

    @typing.override
    def authorization_url(self, state: str) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "prompt": "select_account",
        }
        return f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"

    @typing.override
    async def fetch_identity(self, code: str) -> GoogleIdentity:
        try:
            response = await self.http.post(
                TOKEN_URL,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret.get_secret_value(),
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            response.raise_for_status()
            id_token: str = response.json()["id_token"]

            # PyJWKClient fetches and caches Google's keys with blocking I/O.
            signing_key = await anyio.to_thread.run_sync(
                self.jwks.get_signing_key_from_jwt, id_token
            )
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=ISSUERS,
                options={"require": ["sub", "email", "iss", "aud", "exp"]},
            )
        except (httpx.HTTPError, KeyError, jwt.PyJWTError) as exc:
            raise IdentityProviderError() from exc

        return GoogleIdentity(
            subject=claims["sub"],
            email=claims["email"],
            email_verified=bool(claims.get("email_verified", False)),
            full_name=claims.get("name", "")[:64],
        )
