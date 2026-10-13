"""Load approved sample data into the Find a Time table."""

import json
import sys
from pathlib import Path

from find_a_time.db import (
    DatabaseUnavailableError,
    FindATimeStorage,
    get_dynamodb,
)
from find_a_time.settings import ensure_settings


ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA_PATH = ROOT / "data" / "sample_data.json"


def seed_data(storage: FindATimeStorage) -> None:
    """Load the approved sample records into DynamoDB."""

    print(f"Seeding from {SAMPLE_DATA_PATH} ...")

    # Read the approved sample data.
    with SAMPLE_DATA_PATH.open(encoding="utf-8") as handle:
        items = json.load(handle)

    if not isinstance(items, list):
        raise ValueError("Sample data must be a list.")

    # Check that every record is one of our two supported types.
    for item in items:
        record_type = item.get("record_type")

        if record_type not in ("EVENT", "RESPONSE"):
            raise ValueError(
                f"Unexpected record type: {record_type}"
            )

    # The JSON already matches our DynamoDB record format,
    # so store each record directly.
    for item in items:
        storage.put_item(item)

        print(
            f"Loaded {item['record_id']} "
            f"for event {item['event_id']}"
        )

    print(f"Loaded {len(items)} sample records.")


def main() -> None:
    """Connect to DynamoDB and load the sample data."""

    try:
        # Load our application settings.
        settings = ensure_settings()

        # Connect to the Find a Time table.
        storage = FindATimeStorage(
            table_name=settings["FIND_A_TIME_TABLE_NAME"],
            region_name=settings["AWS_DEFAULT_REGION"],
            endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
        )

        # Make sure the table exists and can be reached.
        storage.ping()

        # Check whether the table already contains data.
        dynamodb = get_dynamodb(settings)
        table = dynamodb.Table(
            settings["FIND_A_TIME_TABLE_NAME"]
        )

        existing = table.scan(
            Select="COUNT",
            Limit=1,
        )

        if existing["Count"] > 0:
            raise RuntimeError(
                "Table already contains data. "
                "Reset it before seeding."
            )

        # Load the approved sample records.
        seed_data(storage)

    except (
        RuntimeError,
        ValueError,
        DatabaseUnavailableError,
    ) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()