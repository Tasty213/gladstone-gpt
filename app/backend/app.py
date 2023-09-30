import logging
import os
import time
import boto3
from uuid import uuid4
import botocore.exceptions
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
from opentelemetry import trace
from OpentelemetryCallback import OpentelemetryCallback
from captcha import captcha_check
from get_local_party_details import get_local_party_details
from schema.canvass import Canvass
from schema.message import Message
from schema.api_question import ApiQuestion
from messageData import MessageData
from canvassData import CanvassData
from query.vortex_query import VortexQuery
from callback import AnswerCallback
from observability import start_opentelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

start_opentelemetry.startup()
tracer = trace.get_tracer("gladstone.app")

botocore.session.get_session()
with tracer.start_as_current_span("app.startup") as span:
    build_dir = os.getenv("BUILD_DIR", "../dist")
    app = FastAPI()

    vector_store = VortexQuery.get_vector_store()

    database_region = os.getenv("DB_REGION", "eu-north-1")
    database_name_canvass = os.getenv("DB_NAME_CANVASS", "canvassData")
    database_name_message = os.getenv("DB_NAME_MESSAGE", "messages")
    canvassDataTable = CanvassData(
        boto3.resource("dynamodb", region_name=database_region).Table(
            database_name_canvass
        )
    )
    messageDataTable = MessageData(
        boto3.resource("dynamodb", region_name=database_region).Table(
            database_name_message
        )
    )


@tracer.start_as_current_span("app.chat")
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive and send back the client message
        question = await websocket.receive_json()
        captcha_check(question.get("captcha"), websocket.client)

        stream_handler = AnswerCallback(websocket)
        otel_handler = OpentelemetryCallback()
        qa_chain = VortexQuery.make_chain(
            vector_store,
            otel_handler,
            stream_handler,
            question.get("local_party_details"),
            os.getenv("k", "4"),
            os.getenv("fetch_k", "20"),
            os.getenv("lambda_mult", "0.5"),
            os.getenv("temperature", "0.7"),
        )

        chat_history: list[Message]
        chat_history = ApiQuestion.from_list(question.get("messages")).message_history

        messageDataTable.add_message(chat_history[-1])

        # Construct a response
        response_message_id = str(uuid4())
        response_message_time = int(time.time() * 1000)
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


@tracer.start_as_current_span("app.submit_canvass")
@app.post("/submit_canvass")
def submit_canvass(canvass: Canvass, request: Request):
    try:
        local_party_details = get_local_party_details(canvass.postcode)

        captcha_check(canvass.captcha, request.client)
        canvassDataTable.add_canvass(
            canvass.userId,
            canvass.firstName,
            canvass.lastName,
            canvass.postcode,
            canvass.email,
            canvass.voterIntent,
            canvass.time,
        )
        return {"status": "SUCCESS", "local_party_details": local_party_details}

    except Exception as e:
        if app.debug:
            raise e
        return {"status": "ERROR", "reason": str(e)}


app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="./localhost-key.pem",
        ssl_certfile="./localhost.pem",
    )
