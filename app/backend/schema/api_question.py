from dataclasses import dataclass
from typing import Self

from schema.message import Message


@dataclass
class ApiQuestion:
    """Class representing a message sent by either a user or the AI"""

    message_history: list[Message]

    @staticmethod
    def from_list(data: list[dict]) -> Self:
        return ApiQuestion([Message.from_dict(message) for message in data])
