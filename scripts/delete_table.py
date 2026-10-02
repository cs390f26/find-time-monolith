"""Safely delete our local Find a Time table."""

import sys

from botocore.exceptions import ClientError

from find_a_time.db import get_dynamodb
from find_a_time.settings import ensure_settings


def _table_exists(dynamodb, table_name: str) -> bool:
    """Check whether the table exists."""

    try:
        dynamodb.meta.client.describe_table(TableName=table_name)
        return True

    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceNotFoundException":
            return False

        raise


def _confirm_delete(table_name: str) -> bool:
    """Ask the user to confirm deletion."""

    answer = input(
        f"Would you like to delete {table_name!r}? "
        "This action cannot be undone. [y/N] "
    ).strip().lower()

    return answer in ("y", "yes")


def delete_table():
    """Delete the local table after confirmation."""

    settings = ensure_settings()
    endpoint = settings["DYNAMODB_ENDPOINT_URL"]

    # Prevent accidental deletion using a non-local address.
    if not endpoint.startswith((
        "http://localhost:",
        "http://127.0.0.1:",
    )):
        raise RuntimeError(
            "Table deletion is restricted to DynamoDB Local."
        )

    dynamodb = get_dynamodb(settings)
    table_name = settings["FIND_A_TIME_TABLE_NAME"]

    if not _table_exists(dynamodb, table_name):
        print(f"Table {table_name!r} does not exist.")
        sys.exit(1)

    if not _confirm_delete(table_name):
        print("Deletion cancelled.")
        sys.exit(1)

    table = dynamodb.Table(table_name)
    table.delete()
    table.wait_until_not_exists()

    print(f"Deleted table {table_name!r}.")


def main():
    """Run the deletion script and report configuration errors."""

    try:
        delete_table()

    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

