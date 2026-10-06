from fastapi.testclient import TestClient

from app.features.domain.constants import Features
from tests.fakes import FakeFeatureFlags


def test_grades_hidden_when_feature_disabled(client: TestClient) -> None:
    response = client.get("/grades/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}


def test_list_grades_when_feature_enabled(
    client: TestClient,
    feature_flags: FakeFeatureFlags,
) -> None:
    feature_flags.flags[Features.GRADES] = True

    response = client.get("/grades/")

    assert response.status_code == 200
    assert response.json() == {"results": [{"subject": "Maths", "value": 11}]}


def test_get_unknown_grade_returns_404(
    client: TestClient,
    feature_flags: FakeFeatureFlags,
) -> None:
    feature_flags.flags[Features.GRADES] = True

    response = client.get("/grades/History")

    assert response.status_code == 404
    assert response.json() == {"detail": "No grade for 'History'"}
