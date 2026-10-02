
"""Connect Find a Time to DynamoDB."""

import boto3

from find_a_time.settings import ensure_settings


def get_dynamodb(settings=None):
    """Return a DynamoDB connection using our app settings."""

    # Load our configuration if it wasn't provided.
    if settings is None:
        settings = ensure_settings()

    # Create a DynamoDB resource using our settings.
    return boto3.resource(
        "dynamodb",
        region_name=settings["AWS_DEFAULT_REGION"],
        endpoint_url=settings["DYNAMODB_ENDPOINT_URL"],
    )


def get_table():
    """Return the configured Find a Time table."""

    # Load the settings and get our database connection.
    settings = ensure_settings()
    dynamodb = get_dynamodb(settings)

    # Return a reference to our table.
    return dynamodb.Table(
        settings["FIND_A_TIME_TABLE_NAME"]
    )
