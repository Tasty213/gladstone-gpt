import logging
from botocore.exceptions import ClientError


class MessageData:
    """Encapsulates an Amazon DynamoDB table of movie data."""

    def __init__(self, table):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.table = table
        self.logger = logging.getLogger()

    def add_message(self, messageId, userId, message, sources, time, previousMessageId):
        try:
            self.table.put_item(
                Item={
                    "messageId": messageId,
                    "userId": userId,
                    "message": message,
                    "sources": sources,
                    "time": time,
                    "previousMessageId": previousMessageId,
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
