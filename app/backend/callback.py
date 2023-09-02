from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
from fastapi import WebSocket

from messageData import MessageData


class QuestionCallback(AsyncCallbackHandler):
    def __init__(self, websocket, message_table: MessageData):
        self.websocket = websocket
        self.message_table = message_table
        super().__init__()

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.message_table.add_message()
        pass


class AnswerCallback(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        super().__init__()

    def save(self, answer):
        pass

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = {"sender": "bot", "message": token, "type": "stream"}
        await self.websocket.send_json(resp)
