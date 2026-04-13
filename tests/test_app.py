import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    original_activities = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = original_activities


@pytest.fixture
def client():
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_activities = app_module.activities

    # Act
    response = client.get("/activities")
    json_data = response.json()

    # Assert
    assert response.status_code == 200
    assert json_data == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "alexandra@mergington.edu"
    assert new_email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    assert duplicate_email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": duplicate_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_missing_activity_returns_404(client):
    # Arrange
    missing_activity = "Space Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{missing_activity}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    assert email in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "noone@mergington.edu"
    assert missing_email not in app_module.activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404(client):
    # Arrange
    missing_activity = "Space Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{missing_activity}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
