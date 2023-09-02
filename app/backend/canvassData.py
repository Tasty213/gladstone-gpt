import logging
import os

from botocore.exceptions import ClientError
from opentelemetry import trace

tracer = trace.get_tracer("gladstone.canvassData")


class CanvassData:
    """Encapsulates an Amazon DynamoDB table of movie data."""

    def __init__(self, table):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.table = table
        self.logger = logging.getLogger()

    def add_canvass(
        self, userId, firstName, lastName, postcode, email, voterIntent, time
    ):
        with tracer.start_as_current_span(
            "gladstone.CanvassData.add_canvass",
            attributes={
                "db.system": "dynamodb",
                "db.name": os.getenv("DB_NAME_CANVASS"),
            },
            kind=trace.SpanKind.CLIENT,
        ):
            try:
                self.table.put_item(
                    Item={
                        "userId": userId,
                        "firstName": firstName,
                        "lastName": lastName,
                        "postcode": postcode,
                        "email": email,
                        "voterIntent": voterIntent,
                        "time": time,
                    }
                )
            except ClientError as err:
                self.logger.error(
                    "Couldn't add canvass %s to table %s. Here's why: %s: %s",
                    userId,
                    self.table.name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
