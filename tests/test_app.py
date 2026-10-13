"""Tests for the Find a Time Flask API."""

import os

os.environ.setdefault(
    "AWS_ACCESS_KEY_ID",
    "test",
)
os.environ.setdefault(
    "AWS_SECRET_ACCESS_KEY",
    "test",
)
os.environ.setdefault(
    "AWS_DEFAULT_REGION",
    "us-east-1",
)
os.environ.setdefault(
    "FIND_A_TIME_TABLE_NAME",
    "FindATimeTest",
)
os.environ.setdefault(
    "DYNAMODB_ENDPOINT_URL",
    "http://127.0.0.1:8000",
)

from find_a_time.app import create_app


def make_client(storage):
    app = create_app(storage)
    app.config["TESTING"] = True

    return app.test_client()


def test_list_events_returns_200(storage):
    client = make_client(storage)

    response = client.get("/api/events")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["events"]) == 1
    assert data["events"][0]["event_name"] == (
        "CS 390 Study Group"
    )
    assert data["events"][0]["response_count"] == 3


def test_get_existing_event_returns_200(storage):
    client = make_client(storage)

    response = client.get("/api/events/2")

    assert response.status_code == 200

    data = response.get_json()

    assert data["event_id"] == 2
    assert data["creator_name"] == "Joshua"
    assert len(data["time_slots"]) == 3


def test_missing_event_returns_404(storage):
    client = make_client(storage)

    response = client.get("/api/events/999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"]["code"] == "EVENT_NOT_FOUND"


def test_invalid_event_creation_returns_400(storage):
    client = make_client(storage)

    response = client.post(
        "/api/events",
        json={
            "event_name": "Bad Event",
            "creator_name": "Clay",
            "time_slots": [
                "2026-10-25T14:00:00-04:00",
            ],
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"]["code"] == (
        "INVALID_TIME_SLOT_COUNT"
    )


def test_invalid_availability_returns_400(storage):
    client = make_client(storage)

    response = client.post(
        "/api/events/2/availability",
        json={
            "participant_name": "Clay",
            "selected_slot_ids": [999],
        },
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["error"]["code"] == "SLOT_NOT_IN_EVENT"


def test_results_returns_aggregated_data(storage):
    client = make_client(storage)

    response = client.get("/api/events/2/results")

    assert response.status_code == 200

    data = response.get_json()

    assert data["response_count"] == 3
    assert data["results"][0]["available_count"] == 2
    assert data["none_available"] == ["Diego"]