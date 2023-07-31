import json
from langchain.schema import AIMessage, HumanMessage, BaseMessage


class MessageFactory:
    @staticmethod
    def create_message(message: dict) -> BaseMessage:
        match message.get("type"):
            case "human":
                return HumanMessage(content=message.get("content"))
            case "ai":
                return AIMessage(content=message.get("content"))
            case _:
                raise ValueError(
                    f"Failed to construct chat message from {json.dumps(message)}"
                )
