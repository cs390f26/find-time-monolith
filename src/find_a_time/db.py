"""DynamoDB storage for Find a Time."""

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import BotoCoreError, ClientError


class DatabaseUnavailableError(Exception):
    """Raised when DynamoDB cannot be reached or used."""


def get_dynamodb(settings):
    """Return a DynamoDB resource using our application settings."""

    return boto3.resource(
        "dynamodb",
        region_name=settings["AWS_DEFAULT_REGION"],
        endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
    )


class FindATimeStorage:
    """Store and retrieve Find a Time records in DynamoDB."""

    def __init__(
        self,
        table_name: str,
        region_name: str,
        endpoint_url: str | None = None,
    ):
        """Connect to the configured DynamoDB table."""

        if not table_name:
            raise ValueError("table_name is required")

        if not region_name:
            raise ValueError("region_name is required")

        if endpoint_url is not None:
            resource = boto3.resource(
                "dynamodb",
                region_name=region_name,
                endpoint_url=endpoint_url,
            )
        else:
            resource = boto3.resource(
                "dynamodb",
                region_name=region_name,
            )

        self._table = resource.Table(table_name)

    def ping(self) -> None:
        """Check that the DynamoDB table is available."""

        try:
            self._table.load()
        except (BotoCoreError, ClientError) as exc:
            raise DatabaseUnavailableError(
                f"database unavailable: {exc}"
            ) from exc

    def get_item(self, key):
        """Return one item by its full DynamoDB key."""

        try:
            response = self._table.get_item(Key=key)
        except (BotoCoreError, ClientError) as exc:
            raise DatabaseUnavailableError(
                f"database unavailable: {exc}"
            ) from exc

        return response.get("Item")

    def put_item(self, item) -> None:
        """Store one item in the table."""

        try:
            self._table.put_item(Item=item)
        except (BotoCoreError, ClientError) as exc:
            raise DatabaseUnavailableError(
                f"database unavailable: {exc}"
            ) from exc

    def get_event(self, event_id: int):
        """Return one event, or None if it does not exist."""

        return self.get_item({
            "event_id": event_id,
            "record_id": "EVENT",
        })

    def list_events(self) -> list[dict]:
        """Return all event records."""

        try:
            items = []

            response = self._table.scan()
            items.extend(response.get("Items", []))

            # DynamoDB scans can return more than one page.
            while "LastEvaluatedKey" in response:
                response = self._table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"]
                )
                items.extend(response.get("Items", []))

        except (BotoCoreError, ClientError) as exc:
            raise DatabaseUnavailableError(
                f"database unavailable: {exc}"
            ) from exc

        events = [
            item
            for item in items
            if item.get("record_type") == "EVENT"
        ]

        return sorted(
            events,
            key=lambda item: int(item["event_id"]),
        )

    def get_responses(self, event_id: int) -> list[dict]:
        """Return all participant responses for one event."""

        try:
            responses = []

            response = self._table.query(
                KeyConditionExpression=(
                    Key("event_id").eq(event_id)
                    & Key("record_id").begins_with("RESPONSE#")
                )
            )

            responses.extend(response.get("Items", []))

            # Keep reading if DynamoDB returns more than one page.
            while "LastEvaluatedKey" in response:
                response = self._table.query(
                    KeyConditionExpression=(
                        Key("event_id").eq(event_id)
                        & Key("record_id").begins_with("RESPONSE#")
                    ),
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                )

                responses.extend(response.get("Items", []))

        except (BotoCoreError, ClientError) as exc:
            raise DatabaseUnavailableError(
                f"database unavailable: {exc}"
            ) from exc

        return sorted(
            responses,
            key=lambda item: int(item["response_id"]),
        )

    def save_event(self, event: dict) -> None:
        """Store an event record."""

        self.put_item(event)

    def save_response(self, response: dict) -> None:
        """Store a participant response."""

        self.put_item(response)