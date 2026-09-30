"""Create the DynamoDB table used by the Find a Time application."""

import boto3

# Load our shared app settings instead of hard-coding values here.
from find_a_time.settings import ensure_settings


def create_table() -> None:
    """Create the Find a Time table if it does not already exist."""

    # Check that all required environment settings are available.
    settings = ensure_settings()

    # Connect to DynamoDB using the configured region and endpoint.
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=settings["AWS_DEFAULT_REGION"],
        endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
    )

    # Keep the table name configurable instead of hard-coding it.
    table_name = settings["FIND_A_TIME_TABLE_NAME"]

    # Get the names of tables that already exist.
    existing_tables = [
        table.name
        for table in dynamodb.tables.all()
    ]

    # Stop if the table already exists so the script can be run again safely.
    if table_name in existing_tables:
        print(f"Table '{table_name}' already exists.")
        return

    # Create one table for both event records and response records.
    # event_id groups everything for the same event.
    # record_id separates the EVENT item from RESPONSE items.
    table = dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                "AttributeName": "event_id",
                "KeyType": "HASH",   # partition key
            },
            {
                "AttributeName": "record_id",
                "KeyType": "RANGE",  # sort key
            },
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "event_id",
                "AttributeType": "N",  # number
            },
            {
                "AttributeName": "record_id",
                "AttributeType": "S",  # string
            },
        ],

        # Let DynamoDB handle capacity instead of setting fixed read/write units.
        BillingMode="PAY_PER_REQUEST",
    )

    # Wait until the table is ready before moving on.
    table.wait_until_exists()

    print(f"Created table '{table_name}'.")


# Run create_table() only when this file is executed directly.
if __name__ == "__main__":
    create_table()
