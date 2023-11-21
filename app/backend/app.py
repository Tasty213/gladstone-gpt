import asyncio
import os
import boto3
import botocore.exceptions
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
from opentelemetry import trace
from query.question_handler import QuestionHandler
from settings.chat_bot_settings import ChatbotSettings
from messageData import MessageData
from query.llm_chain_factory import LLMChainFactory
from observability import start_opentelemetry
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

start_opentelemetry.startup()
tracer = trace.get_tracer("chatbot.app")

botocore.session.get_session()
with tracer.start_as_current_span("app.startup") as span:
    settings_filepath = os.getenv("SETTINGS_FILEPATH", "./settings/test_settings.yaml")
    settings = ChatbotSettings.from_yaml(settings_filepath)

    app = FastAPI()

    vector_store = LLMChainFactory.get_vector_store(settings)

    messageDataTable = MessageData(
        boto3.resource("dynamodb", region_name=settings.database_region).Table(
            settings.database_name_message
        ),
        settings,
    )

    question_handler = QuestionHandler(vector_store, settings, messageDataTable)


@tracer.start_as_current_span("app.chat")
@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        task = question_handler.handle_question(websocket)
        await task
    except (WebSocketDisconnect, ConnectionClosed, ConnectionClosedOK) as e:
        current_span = trace.get_current_span()
        current_span.add_event(
            "websocket closed by client", {"reason": e.reason, "code": e.code}
        )
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
        task.close()
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
