from datetime import datetime
import logging
import os
import boto3
from uuid import uuid4
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
from opentelemetry import trace

from schema.canvass import Canvass
from schema.message import Message
from schema.api_question import ApiQuestion
from messageData import MessageData
from canvassData import CanvassData
from query.vortex_query import VortexQuery
from callback import QuestionCallback, AnswerCallback
from observability.start_opentelemetry import startup

startup()

build_dir = os.getenv("BUILD_DIR", "../dist")
app = FastAPI()

vector_store = VortexQuery().get_vector_store()

database_region = os.getenv("DB_REGION", "eu-north-1")
database_name_canvass = os.getenv("DB_NAME_CANVASS", "canvassData")
database_name_message = os.getenv("DB_NAME_MESSAGE", "messages")
canvassDataTable = CanvassData(
    boto3.resource("dynamodb", region_name=database_region).Table(database_name_canvass)
)
messageDataTable = MessageData(
    boto3.resource("dynamodb", region_name=database_region).Table(database_name_message)
)


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionCallback(websocket, messageDataTable)
    stream_handler = AnswerCallback(websocket)
    qa_chain = VortexQuery.make_chain(vector_store, question_handler, stream_handler)

    try:
        # Receive and send back the client message
        question = await websocket.receive_json()
        chat_history: list[Message]
        chat_history = ApiQuestion.from_list(question).message_history

        messageDataTable.add_message(chat_history[-1])

        # Construct a response
        response_message_id = str(uuid4())
        response_message_time = int(datetime.now().timestamp())
        start_resp = {
            "sender": "bot",
            "messageId": response_message_id,
            "previousMessageId": chat_history[-1].messageId,
            "time": response_message_time,
            "type": "start",
        }
        await websocket.send_json(start_resp)

        result = await qa_chain.acall(
            {
                "question": chat_history[-1].message.content,
                "chat_history": [
                    chat_entry.message for chat_entry in chat_history[:-1]
                ],
            }
        )

        output_message: Message
        output_message = Message.from_langchain_result(
            result.get("answer"),
            result.get("source_documents"),
            chat_history[-1].messageId,
            response_message_id,
            response_message_time,
        )

        await websocket.send_json(
            {
                "sender": "bot",
                "id": output_message.messageId,
                "previousMessageId": output_message.previousMessageId,
                "message": output_message.message.content,
                "sources": output_message.sources,
                "type": "end",
            }
        )

        messageDataTable.add_message(output_message)
    except WebSocketDisconnect:
        logging.info("websocket disconnect")
    except Exception as e:
        logging.error(e)
        resp = {
            "sender": "bot",
            "message": "Sorry, something went wrong. Try again.",
            "type": "error",
        }
        await websocket.send_json(resp)
    finally:
        await websocket.close()


@trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span(
    "/submit_canvass"
)
@app.post("/submit_canvass")
def submit_canvass(canvass: Canvass):
    try:
        canvassDataTable.add_canvass(
            canvass.userId,
            canvass.firstName,
            canvass.lastName,
            canvass.postcode,
            canvass.email,
            canvass.voterIntent,
            canvass.time,
        )
        return {"status": "SUCCESS"}

    except Exception as e:
        if app.debug:
            raise e
        return {"status": "ERROR", "reason": str(e)}


app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="./localhost-key.pem",
        ssl_certfile="./localhost.pem",
    )
