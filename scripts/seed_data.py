"""Load sample-data.json into the table"""

import json
import sys
from pathlib import Path

from src.db import (
    DatabaseUnavailableError,
    FindTimeStorage,
)
from src.dynamo import extract_data
from src.settings import ensure_settings

ROOT = Path(__file__).resolve().parent.parent
SAMPLE_DATA_PATH = ROOT / "data" / "sample_data.json"


def seed_data(storage: FindTimeStorage) -> None:
    with SAMPLE_DATA_PATH.open(encoding="utf-8") as handle:
        items = json.load(handle)

    loaded = 0
    for item in items:
        event = extract_data(item)
        storage.create_event(event)
        loaded += 1
        print(f"  loaded {event.event_id}")

    print(f"Done. loaded={loaded}")


def main() -> None:
    try:
        settings = ensure_settings()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)

    storage = FindTimeStorage(
        table_name=settings["FIND_A_TIME_TABLE_NAME"],
        region_name=settings["AWS_DEFAULT_REGION"],
        endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
    )
    try:
        storage.ping()
    except DatabaseUnavailableError as exc:
        print(
            "Table is missing or unreachable. "
            f"Details: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Seeding from {SAMPLE_DATA_PATH} …")
    seed_data(storage)


if __name__ == "__main__":
    main()
