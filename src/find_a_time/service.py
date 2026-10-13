"""Business logic for the Find a Time application."""

from datetime import datetime

from find_a_time.db import FindATimeStorage


class ValidationError(Exception):
    """Raised when a request contains invalid data."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class EventNotFoundError(Exception):
    """Raised when an event does not exist."""

    def __init__(self):
        super().__init__("Event not found")
        self.code = "EVENT_NOT_FOUND"
        self.message = "Event not found"


class FindATimeService:
    """Apply Find a Time rules using the storage layer."""

    def __init__(self, storage: FindATimeStorage):
        self.storage = storage

    def list_events(self) -> dict:
        """Return event summaries for the Home page."""

        events = self.storage.list_events()
        summaries = []

        for event in events:
            event_id = int(event["event_id"])
            responses = self.storage.get_responses(event_id)

            summaries.append({
                "event_id": event_id,
                "event_name": event["event_name"],
                "creator_name": event["creator_name"],
                "response_count": len(responses),
            })

        return {"events": summaries}

    def get_event(self, event_id: int) -> dict:
        """Return one event for the Submit Availability page."""

        event_id = self._validate_event_id(event_id)

        event = self.storage.get_event(event_id)

        if event is None:
            raise EventNotFoundError()

        return self._event_for_api(event)

    def create_event(
        self,
        event_name,
        creator_name,
        time_slots,
    ) -> dict:
        """Validate and create a new event."""

        event_name = self._validate_name(
            event_name,
            "EVENT_NAME_REQUIRED",
            "Event name is required",
        )

        creator_name = self._validate_name(
            creator_name,
            "CREATOR_NAME_REQUIRED",
            "Creator name is required",
        )

        if time_slots is None:
            raise ValidationError(
                "TIME_SLOTS_REQUIRED",
                "Time slots are required",
            )

        if not isinstance(time_slots, list):
            raise ValidationError(
                "INVALID_REQUEST",
                "Request body is invalid",
            )

        if not 2 <= len(time_slots) <= 10:
            raise ValidationError(
                "INVALID_TIME_SLOT_COUNT",
                "An event must have between 2 and 10 time slots",
            )

        cleaned_times = []
        seen_times = set()

        for start_time in time_slots:
            cleaned_time = self._validate_start_time(start_time)

            if cleaned_time in seen_times:
                raise ValidationError(
                    "DUPLICATE_TIME_SLOT",
                    "Duplicate time slots are not allowed",
                )

            seen_times.add(cleaned_time)
            cleaned_times.append(cleaned_time)

        existing_events = self.storage.list_events()

        event_id = self._next_event_id(existing_events)
        next_slot_id = self._next_slot_id(existing_events)

        stored_slots = []

        for start_time in cleaned_times:
            stored_slots.append({
                "slot_id": next_slot_id,
                "start_time": start_time,
            })

            next_slot_id += 1

        event = {
            "event_id": event_id,
            "record_id": "EVENT",
            "record_type": "EVENT",
            "event_name": event_name,
            "creator_name": creator_name,
            "time_slots": stored_slots,
        }

        self.storage.save_event(event)

        return {"event_id": event_id}

    def submit_availability(
        self,
        event_id: int,
        participant_name,
        selected_slot_ids,
    ) -> dict:
        """Validate and save one participant response."""

        event_id = self._validate_event_id(event_id)

        event = self.storage.get_event(event_id)

        if event is None:
            raise EventNotFoundError()

        participant_name = self._validate_name(
            participant_name,
            "PARTICIPANT_NAME_REQUIRED",
            "Participant name is required",
        )

        if selected_slot_ids is None:
            raise ValidationError(
                "SELECTED_SLOT_IDS_REQUIRED",
                "selected_slot_ids is required",
            )

        if not isinstance(selected_slot_ids, list):
            raise ValidationError(
                "INVALID_REQUEST",
                "Request body is invalid",
            )

        valid_slot_ids = {
            int(slot["slot_id"])
            for slot in event["time_slots"]
        }

        cleaned_slot_ids = []
        seen_slot_ids = set()

        for slot_id in selected_slot_ids:
            if (
                isinstance(slot_id, bool)
                or not isinstance(slot_id, int)
                or slot_id < 1
            ):
                raise ValidationError(
                    "INVALID_SLOT_ID",
                    "Each selected slot id must be a positive integer",
                )

            if slot_id in seen_slot_ids:
                raise ValidationError(
                    "DUPLICATE_SLOT_ID",
                    "A time slot may only be selected once",
                )

            if slot_id not in valid_slot_ids:
                raise ValidationError(
                    "SLOT_NOT_IN_EVENT",
                    "A selected time slot does not belong to this event",
                )

            seen_slot_ids.add(slot_id)
            cleaned_slot_ids.append(slot_id)

        response_id = self._next_response_id()

        response = {
            "event_id": event_id,
            "record_id": f"RESPONSE#{response_id}",
            "record_type": "RESPONSE",
            "response_id": response_id,
            "participant_name": participant_name,
            "selected_slot_ids": cleaned_slot_ids,
        }

        self.storage.save_response(response)

        return {
            "response_id": response_id,
            "message": "Availability submitted",
        }

    def get_results(self, event_id: int) -> dict:
        """Calculate the current availability results for an event."""

        event_id = self._validate_event_id(event_id)

        event = self.storage.get_event(event_id)

        if event is None:
            raise EventNotFoundError()

        responses = self.storage.get_responses(event_id)

        results = []

        for slot in event["time_slots"]:
            slot_id = int(slot["slot_id"])
            participants = []

            for response in responses:
                selected_ids = {
                    int(value)
                    for value in response.get(
                        "selected_slot_ids",
                        [],
                    )
                }

                if slot_id in selected_ids:
                    participants.append(
                        response["participant_name"]
                    )

            results.append({
                "slot_id": slot_id,
                "start_time": slot["start_time"],
                "available_count": len(participants),
                "participants": participants,
            })

        none_available = [
            response["participant_name"]
            for response in responses
            if not response.get("selected_slot_ids", [])
        ]

        return {
            "event_id": event_id,
            "event_name": event["event_name"],
            "creator_name": event["creator_name"],
            "response_count": len(responses),
            "results": results,
            "none_available": none_available,
        }

    def _validate_event_id(self, event_id: int) -> int:
        """Require a positive integer event id."""

        if (
            isinstance(event_id, bool)
            or not isinstance(event_id, int)
            or event_id < 1
        ):
            raise ValidationError(
                "INVALID_EVENT_ID",
                "eventId must be a positive integer",
            )

        return event_id

    def _validate_name(
        self,
        value,
        error_code: str,
        error_message: str,
    ) -> str:
        """Require a nonblank name no longer than 255 characters."""

        if not isinstance(value, str) or not value.strip():
            raise ValidationError(
                error_code,
                error_message,
            )

        value = value.strip()

        if len(value) > 255:
            raise ValidationError(
                "INVALID_REQUEST",
                "Request body is invalid",
            )

        return value

    def _validate_start_time(self, value) -> str:
        """Require a valid ISO 8601 time that starts on the hour."""

        if not isinstance(value, str) or not value.strip():
            raise ValidationError(
                "INVALID_TIME_SLOT",
                "Each time slot must contain a valid date and time",
            )

        value = value.strip()

        # datetime.fromisoformat does not accept Z directly
        # on every supported Python version.
        parse_value = value

        if parse_value.endswith("Z"):
            parse_value = parse_value[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(parse_value)
        except ValueError as exc:
            raise ValidationError(
                "INVALID_TIME_SLOT",
                "Each time slot must contain a valid date and time",
            ) from exc

        # Our API uses complete ISO date-times with a timezone.
        if parsed.tzinfo is None:
            raise ValidationError(
                "INVALID_TIME_SLOT",
                "Each time slot must contain a valid date and time",
            )

        if (
            parsed.minute != 0
            or parsed.second != 0
            or parsed.microsecond != 0
        ):
            raise ValidationError(
                "TIME_NOT_ON_HOUR",
                "Each time slot must start at the top of the hour",
            )

        return value

    def _next_event_id(self, events: list[dict]) -> int:
        """Return the next sequential event id."""

        if not events:
            return 1

        return max(
            int(event["event_id"])
            for event in events
        ) + 1

    def _next_slot_id(self, events: list[dict]) -> int:
        """Return the next sequential slot id."""

        slot_ids = [
            int(slot["slot_id"])
            for event in events
            for slot in event.get("time_slots", [])
        ]

        if not slot_ids:
            return 1

        return max(slot_ids) + 1

    def _next_response_id(self) -> int:
        """Return the next sequential response id."""

        response_ids = []

        for event in self.storage.list_events():
            event_id = int(event["event_id"])

            for response in self.storage.get_responses(event_id):
                response_ids.append(
                    int(response["response_id"])
                )

        # Our approved sample responses begin at 1001.
        if not response_ids:
            return 1001

        return max(response_ids) + 1

    def _event_for_api(self, event: dict) -> dict:
        """Remove DynamoDB-only fields from an event response."""

        return {
            "event_id": int(event["event_id"]),
            "event_name": event["event_name"],
            "creator_name": event["creator_name"],
            "time_slots": [
                {
                    "slot_id": int(slot["slot_id"]),
                    "start_time": slot["start_time"],
                }
                for slot in event["time_slots"]
            ],
        }