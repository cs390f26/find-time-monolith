"""Flask API for the Find a Time application."""

from flask import Flask, jsonify, request

from find_a_time.db import (
    DatabaseUnavailableError,
    FindATimeStorage,
)
from find_a_time.service import (
    EventNotFoundError,
    FindATimeService,
    ValidationError,
)
from find_a_time.settings import ensure_settings


def create_app(storage=None):
    """Create and configure the Flask application."""

    app = Flask(__name__)

    # Normal application startup uses the configured DynamoDB table.
    # Tests can provide a different storage object if needed.
    if storage is None:
        settings = ensure_settings()

        storage = FindATimeStorage(
            table_name=settings["FIND_A_TIME_TABLE_NAME"],
            region_name=settings["AWS_DEFAULT_REGION"],
            endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
        )

    service = FindATimeService(storage)

    def get_json_body():
        """Return a JSON request body or raise a validation error."""

        body = request.get_json(silent=True)

        if not isinstance(body, dict):
            raise ValidationError(
                "INVALID_REQUEST",
                "Request body is invalid",
            )

        return body

    def parse_event_id(value):
        """Convert a URL event id into a positive integer."""

        try:
            event_id = int(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                "INVALID_EVENT_ID",
                "eventId must be a positive integer",
            ) from exc

        if event_id < 1:
            raise ValidationError(
                "INVALID_EVENT_ID",
                "eventId must be a positive integer",
            )

        return event_id

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc):
        """Return application validation errors as HTTP 400."""

        return jsonify({
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }), 400

    @app.errorhandler(EventNotFoundError)
    def handle_event_not_found(exc):
        """Return missing events as HTTP 404."""

        return jsonify({
            "error": {
                "code": exc.code,
                "message": exc.message,
            }
        }), 404

    @app.errorhandler(DatabaseUnavailableError)
    def handle_database_unavailable(exc):
        """Return database failures as HTTP 503."""

        return jsonify({
            "error": {
                "code": "SERVICE_UNAVAILABLE",
                "message": "Service unavailable",
            }
        }), 503

    @app.errorhandler(500)
    def handle_internal_server_error(exc):
        """Return unexpected failures without exposing internals."""

        return jsonify({
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred",
            }
        }), 500

    @app.get("/health")
    def health():
        """Return whether the application and database are available."""

        try:
            storage.ping()
        except DatabaseUnavailableError:
            return jsonify({
                "status": "unavailable",
            }), 503

        return jsonify({
            "status": "ok",
        }), 200

    @app.get("/api/events")
    def list_events():
        """Return event summaries for the Home page."""

        return jsonify(service.list_events()), 200

    @app.post("/api/events")
    def create_event():
        """Create a new event."""

        body = get_json_body()

        result = service.create_event(
            body.get("event_name"),
            body.get("creator_name"),
            body.get("time_slots"),
        )

        return jsonify(result), 201

    @app.get("/api/events/<event_id>")
    def get_event(event_id):
        """Return one event for the Submit Availability page."""

        event_id = parse_event_id(event_id)

        return jsonify(
            service.get_event(event_id)
        ), 200

    @app.post("/api/events/<event_id>/availability")
    def submit_availability(event_id):
        """Store one participant's availability response."""

        event_id = parse_event_id(event_id)
        body = get_json_body()

        result = service.submit_availability(
            event_id,
            body.get("participant_name"),
            body.get("selected_slot_ids"),
        )

        return jsonify(result), 201

    @app.get("/api/events/<event_id>/results")
    def get_results(event_id):
        """Return calculated availability results."""

        event_id = parse_event_id(event_id)

        return jsonify(
            service.get_results(event_id)
        ), 200

    return app


app = create_app()