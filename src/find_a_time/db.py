
"""Connect Find a Time to DynamoDB."""

import boto3

class FindATimeStorage:

    def __init__(
        self,
        table_name: str,
        region_name: str,
        endpoint_url: str | None = None,
    ):
        """Connect to a DynamoDB table.

        table_name: name of the Find-A-Time table
        region_name: AWS region (always required)
        endpoint_url: DynamoDB Local URL, or omit for Amazon DynamoDB
        """

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
        self._table.load()

    def get_item(self, key):
    """Return an item from the table."""
        response = self._table.get_item(Key=key)
        return response.get("Item")
