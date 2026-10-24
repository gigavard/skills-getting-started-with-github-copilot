import src.app as app_module
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn chess",
            "schedule": "Fridays",
            "max_participants": 12,
            "participants": ["alex@example.com"],
        },
        "Art Club": {
            "description": "Make art",
            "schedule": "Wednesdays",
            "max_participants": 10,
            "participants": [],
        },
    }
    monkeypatch.setattr(app_module, "activities", test_activities)
    return TestClient(app_module.app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert set(response.json()) == {"Chess Club", "Art Club"}


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up sam@example.com for Art Club"}
    activities_response = client.get("/activities")
    assert activities_response.json()["Art Club"]["participants"] == ["sam@example.com"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_without_mutating_participants(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Student is already signed up for this activity"
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == ["alex@example.com"]


def test_remove_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Removed alex@example.com from Chess Club"}
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == []


def test_remove_participant_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants",
        params={"email": "alex@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_returns_404_when_not_signed_up(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "sam@example.com"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
    activities_response = client.get("/activities")
    assert activities_response.json()["Chess Club"]["participants"] == ["alex@example.com"]