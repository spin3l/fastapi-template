from fastapi.testclient import TestClient

from app.auth.application.ports.google_oauth import GoogleIdentity
from tests.fakes import FakeGoogleOAuthClient


def _register(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={"email": "ada@example.com", "fullName": "Ada", "password": "s3cret-pass"},
    )
    assert response.status_code == 201, response.text


def _login(client: TestClient) -> str:
    response = client.post(
        "/auth/login", data={"username": "ada@example.com", "password": "s3cret-pass"}
    )
    assert response.status_code == 200, response.text
    assert response.json()["token_type"] == "bearer"
    return str(response.json()["access_token"])


def test_register_login_and_me(client: TestClient) -> None:
    _register(client)
    token = _login(client)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "email": "ada@example.com",
        "fullName": "Ada",
        "isActive": True,
    }


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/auth/register",
        json={"email": "ada@example.com", "fullName": "Ada", "password": "s3cret-pass"},
    )

    assert response.status_code == 409


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    _register(client)

    response = client.post(
        "/auth/login", data={"username": "ada@example.com", "password": "wrong-pass"}
    )

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_me_requires_valid_token(client: TestClient) -> None:
    assert client.get("/auth/me").status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_google_login_redirects_with_state_cookie(client: TestClient) -> None:
    response = client.get("/auth/google/login", follow_redirects=False)

    assert response.status_code == 307
    state = response.cookies["google_oauth_state"]
    assert response.headers["location"].endswith(f"state={state}")


def test_google_callback_issues_token(
    client: TestClient, google_oauth: FakeGoogleOAuthClient
) -> None:
    google_oauth.identities["code"] = GoogleIdentity(
        subject="google-123", email="ada@example.com", email_verified=True, full_name="Ada"
    )
    client.get("/auth/google/login", follow_redirects=False)
    state = client.cookies["google_oauth_state"]

    response = client.get("/auth/google/callback", params={"code": "code", "state": state})

    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["email"] == "ada@example.com"


def test_google_callback_rejects_state_mismatch(client: TestClient) -> None:
    client.get("/auth/google/login", follow_redirects=False)

    response = client.get("/auth/google/callback", params={"code": "code", "state": "forged"})

    assert response.status_code == 400


def test_google_callback_with_bad_code_returns_401(client: TestClient) -> None:
    client.get("/auth/google/login", follow_redirects=False)
    state = client.cookies["google_oauth_state"]

    response = client.get("/auth/google/callback", params={"code": "bad", "state": state})

    assert response.status_code == 401
