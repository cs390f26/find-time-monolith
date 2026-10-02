
"""Create the DynamoDB table used by the Find a Time application."""

# Use our shared database connection instead of creating a separate one.
from find_a_time.db import get_dynamodb
from find_a_time.settings import ensure_settings


def create_table() -> None:
    """Create the Find a Time table if it does not already exist."""

    # Check that all required environment settings are available.
    settings = ensure_settings()

    # Reuse our shared DynamoDB connection.
    dynamodb = get_dynamodb(settings)

    # Keep the table name configurable instead of hard-coding it.
    table_name = settings["FIND_A_TIME_TABLE_NAME"]

    # Get the names of tables that already exist.
    existing_tables = [
        table.name
        for table in dynamodb.tables.all()
    ]

    # Stop if the table already exists so the script can run again safely.
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
                "KeyType": "HASH",  # Partition key
            },
            {
                "AttributeName": "record_id",
                "KeyType": "RANGE",  # Sort key
            },
        ],
        AttributeDefinitions=[
            {
                "AttributeName": "event_id",
                "AttributeType": "N",  # Number
            },
            {
                "AttributeName": "record_id",
                "AttributeType": "S",  # String
            },
        ],

        # Let DynamoDB manage capacity instead of setting fixed units.
        BillingMode="PAY_PER_REQUEST",
    )

    # Wait until the table is ready before continuing.
    table.wait_until_exists()

    print(f"Created table '{table_name}'.")


# Run the function only when this script is executed directly.
if __name__ == "__main__":
    create_table()
