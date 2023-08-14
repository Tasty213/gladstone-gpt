from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
import logging
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
import os
import boto3
from flask import Flask, request, jsonify
from backend.messageData import MessageData
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from backend.canvassData import CanvassData
from backend.query.vortex_query import VortexQuery
from flask import Flask, jsonify, request
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
import uuid

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

# Initialize metering and an exporter that can send data to an OTLP endpoint
# SELECT count(`http.server.active_requests`) FROM Metric FACET `service.name` TIMESERIES
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
# Logs # - OpenTelemetry Logs are still in the experimental state, so function names may change in the future
########
logging.basicConfig(level=logging.DEBUG)


# Initialize logging and an exporter that can send data to an OTLP endpoint by attaching OTLP handler to root logger
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

build_dir = os.getenv("BUILD_DIR", "dist")
app = Flask(__name__, static_folder=f"../{build_dir}", static_url_path="/")
FlaskInstrumentor().instrument_app(app)

query = VortexQuery()

database_region = os.getenv("DB_REGION", "eu-north-1")
database_name_canvass = os.getenv("DB_NAME_CANVASS", "canvassData")
database_name_message = os.getenv("DB_NAME_MESSAGE", "messages")
canvassDataTable = CanvassData(
    boto3.resource("dynamodb", region_name=database_region).Table(database_name_canvass)
)
messageDataTable = MessageData(
    boto3.resource("dynamodb", region_name=database_region).Table(database_name_message)
)


@trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span("/")
@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


@trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span(
    "/get_response"
)
@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        return jsonify(query.ask_question(request.get_json(), messageDataTable))
    except Exception as e:
        if app.debug:
            raise e
        return jsonify({"status": "ERROR", "reason": str(e)})


@trace.get_tracer("opentelemetry.instrumentation.custom").start_as_current_span(
    "/submit_canvass"
)
@app.route("/submit_canvass", methods=["POST"])
def submit_canvass():
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
        return jsonify({"status": "SUCCESS"})

    except Exception as e:
        if app.debug:
            raise e
        return jsonify({"status": "ERROR", "reason": str(e)})
