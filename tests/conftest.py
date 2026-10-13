"""Shared test fixtures for Find a Time."""

import pytest


class FakeStorage:
    """Small in-memory replacement for DynamoDB during tests."""

    def __init__(self):
        self.events = [
            {
                "event_id": 2,
                "record_id": "EVENT",
                "record_type": "EVENT",
                "event_name": "CS 390 Study Group",
                "creator_name": "Joshua",
                "time_slots": [
                    {
                        "slot_id": 3,
                        "start_time": "2026-09-28T16:00:00-04:00",
                    },
                    {
                        "slot_id": 4,
                        "start_time": "2026-09-29T16:00:00-04:00",
                    },
                    {
                        "slot_id": 5,
                        "start_time": "2026-09-30T18:00:00-04:00",
                    },
                ],
            }
        ]

        self.responses = [
            {
                "event_id": 2,
                "record_id": "RESPONSE#1001",
                "record_type": "RESPONSE",
                "response_id": 1001,
                "participant_name": "Clannys",
                "selected_slot_ids": [3, 5],
            },
            {
                "event_id": 2,
                "record_id": "RESPONSE#1002",
                "record_type": "RESPONSE",
                "response_id": 1002,
                "participant_name": "Alex",
                "selected_slot_ids": [3, 4, 5],
            },
            {
                "event_id": 2,
                "record_id": "RESPONSE#1003",
                "record_type": "RESPONSE",
                "response_id": 1003,
                "participant_name": "Diego",
                "selected_slot_ids": [],
            },
        ]

    def ping(self):
        """Pretend the database is available."""

    def list_events(self):
        return list(self.events)

    def get_event(self, event_id):
        for event in self.events:
            if event["event_id"] == event_id:
                return event

        return None

    def get_responses(self, event_id):
        return [
            response
            for response in self.responses
            if response["event_id"] == event_id
        ]

    def save_event(self, event):
        self.events.append(event)

    def save_response(self, response):
        self.responses.append(response)


@pytest.fixture
def storage():
    """Return a fresh fake database for every test."""

    return FakeStorage()