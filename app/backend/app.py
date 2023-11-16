import logging
import os
import time
import boto3
from uuid import uuid4
import botocore.exceptions
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
from opentelemetry import trace
from OpentelemetryCallback import OpentelemetryCallback
from settings.gladstone_settings import GladstoneSettings
from captcha import captcha_check
from schema.message import Message
from schema.api_question import ApiQuestion
from messageData import MessageData
from query.vortex_query import VortexQuery
from callback import AnswerCallback
from observability import start_opentelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from langchain.callbacks import get_openai_callback

start_opentelemetry.startup()
tracer = trace.get_tracer("gladstone.app")

botocore.session.get_session()
with tracer.start_as_current_span("app.startup") as span:
    settings_filepath = os.getenv("SETTINGS_FILEPATH", "./settings/test_settings.yaml")
    settings = GladstoneSettings.from_yaml(settings_filepath)

    app = FastAPI()

    vector_store = VortexQuery.get_vector_store(settings)

    messageDataTable = MessageData(
        boto3.resource("dynamodb", region_name=settings.database_region).Table(
            settings.database_name_message
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
            settings,
            settings.documents_returned,
            settings.documents_considered,
            settings.lambda_mult,
            settings.temperature,
        )

        chat_history: list[Message]
        chat_history = ApiQuestion.from_list(question.get("messages")).message_history

        messageDataTable.add_message(chat_history[-1], settings)

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

        with get_openai_callback() as cb:
            result = await qa_chain.acall(
                {
                    "question": chat_history[-1].message.content,
                    "chat_history": [
                        chat_entry.message for chat_entry in chat_history[:-1]
                    ],
                }
            )
            current_span = trace.get_current_span()
            current_span.add_event(
                "message_complete",
                {"total_tokens": cb.total_tokens, "total_cost": cb.total_cost},
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

        messageDataTable.add_message(output_message, settings)
    except WebSocketDisconnect:
        logging.info("websocket disconnect")
    except Exception as e:
        current_span = trace.get_current_span()
        current_span.record_exception(e)
        resp = {
            "sender": "bot",
            "message": "Sorry, something went wrong. Try again.",
            "type": "error",
        }
        await websocket.send_json(resp)
    finally:
        await websocket.close()


app.mount(
    "/", StaticFiles(directory=settings.build_directory, html=True), name="static"
)

FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        ssl_keyfile="./localhost-key.pem",
        ssl_certfile="./localhost.pem",
    )
