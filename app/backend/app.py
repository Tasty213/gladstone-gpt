from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource

import logging
import os
import boto3
import uuid

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn

from schema.message import Message
from schema.api_question import ApiQuestion
from messageData import MessageData
from canvassData import CanvassData
from query.vortex_query import VortexQuery
from callback import QuestionCallback, AnswerCallback

##########################
# OpenTelemetry Settings #
##########################

OTEL_RESOURCE_ATTRIBUTES = {
    "service.instance.id": str(uuid.uuid1()),
    "environment": "local",
}

##########
# Traces #
##########

# Initialize tracing and an exporter that can send data to an OTLP endpoint
# SELECT * FROM Span WHERE instrumentation.provider='opentelemetry'
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create(OTEL_RESOURCE_ATTRIBUTES))
)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

###########
# Metrics #
###########

# Initialize metering and an exporter that can send data to an OTLP endpoint example
# NRQL:
# SELECT count(`http.server.active_requests`)
# FROM Metric
# FACET `service.name`
# TIMESERIES
metrics.set_meter_provider(
    MeterProvider(
        resource=Resource.create(OTEL_RESOURCE_ATTRIBUTES),
        metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
    )
)
metrics.get_meter_provider()
fib_counter = metrics.get_meter("opentelemetry.instrumentation.custom").create_counter(
    "fibonacci.invocations",
    unit="1",
    description="Measures the number of times the fibonacci method is invoked.",
)

########
# Logs # - OpenTelemetry Logs are still in the experimental state, so function names
# may change in the future
# ########
logging.basicConfig(level=logging.DEBUG)


# Initialize logging and an exporter that can send data to an OTLP endpoint by attaching
#  OTLP handler to root logger
# SELECT * FROM Log WHERE instrumentation.provider='opentelemetry'
_logs.set_logger_provider(
    LoggerProvider(resource=Resource.create(OTEL_RESOURCE_ATTRIBUTES))
)
logging.getLogger().addHandler(
    LoggingHandler(
        logger_provider=_logs.get_logger_provider().add_log_record_processor(
            BatchLogRecordProcessor(OTLPLogExporter())
        )
    )
)

#####################
# Flask Application #
#####################

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
        start_resp = {"sender": "bot", "message": "", "type": "start"}
        await websocket.send_json(start_resp)

        result = await qa_chain.acall(
            {
                "question": chat_history[-1].message.content,
                "chat_history": [
                    chat_entry.message.content for chat_entry in chat_history[:-1]
                ],
            }
        )
        messageDataTable.add_message(
            Message.from_langchain_result(
                result.get("answer"),
                result.get("source_documents"),
                chat_history[-1].messageId,
            )
        )
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
        end_resp = {"sender": "bot", "message": "", "type": "end"}
        await websocket.send_json(end_resp)
        await websocket.close()


@trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span(
    "/submit_canvass"
)
@app.route("/submit_canvass", methods=["POST"])
def submit_canvass(request):
    try:
        data = request.get_json()
        canvassDataTable.add_canvass(
            data.get("userId"),
            data.get("firstName"),
            data.get("lastName"),
            data.get("postcode"),
            data.get("email"),
            data.get("voterIntent"),
            data.get("time"),
        )
        return {"status": "SUCCESS"}

    except Exception as e:
        if app.debug:
            raise e
        return {"status": "ERROR", "reason": str(e)}


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


# def test_websocket():
#     client = TestClient(app)
#     with client.websocket_connect("/chat") as websocket:
#         data = websocket.receive_json()
#         assert data == {"msg": "Hello WebSocket"}


app.mount("/", StaticFiles(directory=build_dir), name="static")

# test_websocket()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
