from langchain.callbacks.base import AsyncCallbackHandler
from fastapi import WebSocket
from typing import Any


class StreamingCallback(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        super().__init__()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = {"sender": "bot", "message": token, "type": "stream"}
        await self.websocket.send_json(resp)
