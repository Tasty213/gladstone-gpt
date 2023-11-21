import logging

from botocore.exceptions import ClientError
from opentelemetry import trace
from settings.chat_bot_settings import ChatbotSettings

from schema.api_question import Message

tracer = trace.get_tracer("chatbot.messageData")


class MessageData:
    """Encapsulates an Amazon DynamoDB table of movie data."""

    def __init__(self, table):
        """
        :param dyn_resource: A Boto3 DynamoDB resource.
        """
        self.table = table
        self.logger = logging.getLogger()

    def add_message(self, question: Message, settings: ChatbotSettings):
        with tracer.start_as_current_span(
            "chatbot.MessageData.add_message",
            attributes={
                "db.system": "dynamodb",
                "db.name": settings.database_name_message,
            },
            kind=trace.SpanKind.CLIENT,
        ):
            try:
                self.table.put_item(
                    Item={
                        "messageId": question.messageId,
                        "userId": question.user,
                        "message": question.message.content,
                        "sources": question.sources,
                        "time": question.time,
                        "previousMessageId": question.previousMessageId,
                    }
                )
            except ClientError as err:
                self.logger.error(
                    "Couldn't add canvass %s to table %s. Here's why: %s: %s",
                    question.user,
                    self.table.name,
                    err.response["Error"]["Code"],
                    err.response["Error"]["Message"],
                )
                raise
