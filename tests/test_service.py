"""Tests for Find a Time business logic."""

import pytest

from find_a_time.service import (
    FindATimeService,
    ValidationError,
)


def test_get_results_aggregates_responses(storage):
    service = FindATimeService(storage)

    results = service.get_results(2)

    assert results["event_name"] == "CS 390 Study Group"
    assert results["creator_name"] == "Joshua"
    assert results["response_count"] == 3

    assert results["results"][0]["available_count"] == 2
    assert results["results"][0]["participants"] == [
        "Clannys",
        "Alex",
    ]

    assert results["results"][1]["available_count"] == 1
    assert results["results"][1]["participants"] == [
        "Alex",
    ]

    assert results["none_available"] == ["Diego"]


def test_create_event_rejects_too_few_times(storage):
    service = FindATimeService(storage)

    with pytest.raises(ValidationError) as exc:
        service.create_event(
            "Test Event",
            "Clay",
            [
                "2026-10-25T14:00:00-04:00",
            ],
        )

    assert exc.value.code == "INVALID_TIME_SLOT_COUNT"


def test_submit_availability_rejects_unknown_slot(storage):
    service = FindATimeService(storage)

    with pytest.raises(ValidationError) as exc:
        service.submit_availability(
            2,
            "Clay",
            [999],
        )

    assert exc.value.code == "SLOT_NOT_IN_EVENT"


def test_submit_empty_availability_is_valid(storage):
    service = FindATimeService(storage)

    result = service.submit_availability(
        2,
        "No Times User",
        [],
    )

    assert result["message"] == "Availability submitted"

    saved_response = storage.responses[-1]

    assert saved_response["participant_name"] == "No Times User"
    assert saved_response["selected_slot_ids"] == []