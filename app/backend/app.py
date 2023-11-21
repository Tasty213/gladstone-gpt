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
from settings.chat_bot_settings import ChatbotSettings
from captcha import QuestionTooLongError, captcha_check, throw_on_long_question
from schema.message import Message
from schema.api_question import ApiQuestion
from messageData import MessageData
from query.vortex_query import VortexQuery
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from callback import AnswerCallback
from observability import start_opentelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from langchain.callbacks.openai_info import OpenAICallbackHandler
from websockets.exceptions import ConnectionClosed

start_opentelemetry.startup()
tracer = trace.get_tracer("chatbot.app")

botocore.session.get_session()
with tracer.start_as_current_span("app.startup") as span:
    settings_filepath = os.getenv("SETTINGS_FILEPATH", "./settings/test_settings.yaml")
    settings = ChatbotSettings.from_yaml(settings_filepath)

    app = FastAPI()
    app.add_middleware(HTTPSRedirectMiddleware)

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
        throw_on_long_question(question)

        stream_handler = AnswerCallback(websocket)
        otel_handler = OpentelemetryCallback()
        open_ai_costings_handler = OpenAICallbackHandler()
        qa_chain = VortexQuery.make_chain(
            vector_store,
            open_ai_costings_handler,
            otel_handler,
            stream_handler,
            question.get("local_party_details"),
            settings,
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
            {
                "total_tokens": open_ai_costings_handler.total_tokens,
                "total_cost": open_ai_costings_handler.total_cost,
            },
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
    except WebSocketDisconnect as e:
        current_span = trace.get_current_span()
        current_span.add_event(
            "websocket closed by client", {"reason": e.reason, "code": e.code}
        )
    except ConnectionClosed as e:
        current_span = trace.get_current_span()
        current_span.add_event(
            "websocket connection closed", {"reason": e.reason, "code": e.code}
        )
    except QuestionTooLongError as e:
        current_span = trace.get_current_span()
        current_span.record_exception(e)
        resp = {
            "sender": "bot",
            "message": "Your question was too long to be processed, please phrase your question in less that 250 characters.",
            "type": "error",
        }
        await websocket.send_json(resp)

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
