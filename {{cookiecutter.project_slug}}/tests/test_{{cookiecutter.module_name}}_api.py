from fastapi.testclient import TestClient

from app.features.domain.constants import Features
from tests.fakes import FakeFeatureFlags


def test_{{ cookiecutter.module_name }}_hidden_when_feature_disabled(client: TestClient) -> None:
    response = client.get("/{{ cookiecutter.module_name }}/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_list_{{ cookiecutter.module_name }}_when_feature_enabled(
    client: TestClient,
    feature_flags: FakeFeatureFlags,
) -> None:
    feature_flags.flags[Features.{{ cookiecutter.module_name.upper() }}] = True

    response = client.get("/{{ cookiecutter.module_name }}/")

    assert response.status_code == 200
    assert response.json() == {"results": [{"name": "example", "value": 1}]}


def test_get_unknown_{{ cookiecutter.entity_name }}_returns_404(
    client: TestClient,
    feature_flags: FakeFeatureFlags,
) -> None:
    feature_flags.flags[Features.{{ cookiecutter.module_name.upper() }}] = True

    response = client.get("/{{ cookiecutter.module_name }}/missing")

    assert response.status_code == 404
    assert response.json() == {"detail": "No {{ cookiecutter.__entity_label }} for 'missing'"}
