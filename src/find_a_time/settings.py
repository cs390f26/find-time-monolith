"""Load and validate the settings needed by Find a Time."""

import os

from dotenv import load_dotenv


REQUIRED_SETTINGS = (
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_DEFAULT_REGION",
    "FIND_A_TIME_TABLE_NAME",
    "DYNAMODB_ENDPOINT_URL",
)


def ensure_settings() -> dict[str, str]:
    """Load environment settings and make sure required values exist."""

    load_dotenv()

    missing = [
        name
        for name in REQUIRED_SETTINGS
        if not os.environ.get(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing required settings: " + ", ".join(missing)
        )

    return {
        name: os.environ[name]
        for name in REQUIRED_SETTINGS
    }
