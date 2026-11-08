import pytest
from fastapi.testclient import TestClient

from app.auth.domain.roles import Role
from app.features.domain.constants import Features

# Sorted separately so the import order doesn't depend on the module name.
# isort: split
from app.{{ cookiecutter.module_name }}.domain.{{ cookiecutter.entity_name }} import RESOURCE_TYPE
from tests.fakes import FakeFeatureFlags, InMemoryUserRepository

PASSWORD = "s3cret-pass"
ITEM_URL = "/{{ cookiecutter.module_name }}/example"


def _signup(
    client: TestClient,
    users: InMemoryUserRepository,
    name: str,
    role: Role = Role.USER,
) -> tuple[int, dict[str, str]]:
    """Registers a user, sets its role directly in the fake repo, returns (id, auth headers)."""
    email = f"{name}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "fullName": name, "password": PASSWORD},
    )
    assert response.status_code == 201, response.text
    user_id = int(response.json()["id"])
    users.users[user_id].role = role

    response = client.post("/auth/login", data={"username": email, "password": PASSWORD})
    assert response.status_code == 200, response.text
    return user_id, {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(autouse=True)
def _enable_module(feature_flags: FakeFeatureFlags) -> None:
    feature_flags.flags[Features.{{ cookiecutter.module_name.upper() }}] = True


def test_admin_sets_role(client: TestClient, users: InMemoryUserRepository) -> None:
    _, admin = _signup(client, users, "admin", Role.ADMIN)
    ada_id, _ = _signup(client, users, "ada")

    response = client.patch(f"/users/{ada_id}/role", json={"role": "user_admin"}, headers=admin)

    assert response.status_code == 200, response.text
    assert response.json()["role"] == "user_admin"


def test_non_admin_cannot_set_role(client: TestClient, users: InMemoryUserRepository) -> None:
    ada_id, ada = _signup(client, users, "ada", Role.USER_ADMIN)

    response = client.patch(f"/users/{ada_id}/role", json={"role": "admin"}, headers=ada)

    assert response.status_code == 403
    assert response.json() == {"detail": "Not enough permissions", "code": "forbidden"}


def test_invalid_role_is_rejected(client: TestClient, users: InMemoryUserRepository) -> None:
    _, admin = _signup(client, users, "admin", Role.ADMIN)
    ada_id, _ = _signup(client, users, "ada")

    response = client.patch(f"/users/{ada_id}/role", json={"role": "root"}, headers=admin)

    assert response.status_code == 422


def test_grant_lifecycle(client: TestClient, users: InMemoryUserRepository) -> None:
    _, admin = _signup(client, users, "admin", Role.ADMIN)
    ua_id, _ = _signup(client, users, "ua", Role.USER_ADMIN)
    grant = {"resourceType": RESOURCE_TYPE, "resourceId": "example"}

    assert client.post(f"/users/{ua_id}/grants", json=grant, headers=admin).status_code == 201
    assert client.get(f"/users/{ua_id}/grants", headers=admin).json() == [grant]

    url = f"/users/{ua_id}/grants/{RESOURCE_TYPE}/example"
    assert client.delete(url, headers=admin).status_code == 204
    assert client.get(f"/users/{ua_id}/grants", headers=admin).json() == []


def test_admin_updates_any_resource(client: TestClient, users: InMemoryUserRepository) -> None:
    _, admin = _signup(client, users, "admin", Role.ADMIN)

    response = client.put(ITEM_URL, json={"value": 7}, headers=admin)

    assert response.status_code == 200, response.text
    assert response.json() == {"name": "example", "value": 7}


def test_user_admin_needs_a_grant(client: TestClient, users: InMemoryUserRepository) -> None:
    _, admin = _signup(client, users, "admin", Role.ADMIN)
    ua_id, user_admin = _signup(client, users, "ua", Role.USER_ADMIN)

    assert client.put(ITEM_URL, json={"value": 7}, headers=user_admin).status_code == 403

    grant = {"resourceType": RESOURCE_TYPE, "resourceId": "example"}
    assert client.post(f"/users/{ua_id}/grants", json=grant, headers=admin).status_code == 201

    assert client.put(ITEM_URL, json={"value": 7}, headers=user_admin).status_code == 200


def test_plain_user_cannot_update(client: TestClient, users: InMemoryUserRepository) -> None:
    _, ada = _signup(client, users, "ada")

    assert client.put(ITEM_URL, json={"value": 7}, headers=ada).status_code == 403


def test_update_requires_authentication(client: TestClient) -> None:
    assert client.put(ITEM_URL, json={"value": 7}).status_code == 401
