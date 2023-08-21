from dataclasses import dataclass
from datetime import datetime
from typing import Self
from uuid import uuid4

from langchain.schema import BaseMessage, AIMessage, HumanMessage, Document


@dataclass
class Message:
    """Class representing a message sent by either a user or the AI"""

    message: BaseMessage
    messageId: str
    previousMessageId: str
    sources: list[dict] | None
    user: str
    time: str
    sender_type: str

    @staticmethod
    def from_dict(data: dict) -> Self:
        return Message(
            message=Message._get_typed_message(
                data.get("content"), data.get("type"), data.get("messageId")
            ),
            messageId=data.get("messageId"),
            previousMessageId=data.get("previousMessageId"),
            sources=data.get("sources"),
            user=data.get("user"),
            time=data.get("time"),
            sender_type=data.get("type"),
        )

    @staticmethod
    def from_langchain_result(
        message: str, sources: list[Document], previousMessageId: str
    ) -> Self:
        return Message(
            message=AIMessage(content=message),
            messageId=str(uuid4()),
            previousMessageId=previousMessageId,
            sources=[source.metadata for source in sources],
            user="AI",
            time=str(datetime.now()),
            sender_type="AI",
        )

    @staticmethod
    def _get_typed_message(message, sender_type, id) -> BaseMessage:
        match sender_type:
            case "human":
                return HumanMessage(content=message)
            case "ai":
                return AIMessage(content=message)
            case _:
                raise ValueError(
                    f"Failed to construct chat message for message {id} with type {sender_type} and content {message}"
                )
