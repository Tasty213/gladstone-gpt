from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry import _logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.trace import Tracer
from opentelemetry import trace

import logging

from observability.heroku_detector import HerokuResourceDetector


def startup() -> None:
    otel_resource_attributes = HerokuResourceDetector()
    tracer_provider = TracerProvider(resource=otel_resource_attributes.detect())
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    metrics.set_meter_provider(
        MeterProvider(
            resource=otel_resource_attributes.detect(),
            metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
        )
    )

    logging.basicConfig(level=logging.DEBUG)
    logger_provider = LoggerProvider(resource=otel_resource_attributes.detect())
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))

    _logs.set_logger_provider(logger_provider)

    logging.getLogger().addHandler(LoggingHandler(logger_provider=logger_provider))
