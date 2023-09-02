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
from opentelemetry import trace

import logging

from heroku_detector import HerokuResourceDetector


def startup():
    OTEL_RESOURCE_ATTRIBUTES = HerokuResourceDetector()

    trace.set_tracer_provider(
        TracerProvider(resource=OTEL_RESOURCE_ATTRIBUTES.detect()).add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter())
        )
    )

    metrics.set_meter_provider(
        MeterProvider(
            resource=OTEL_RESOURCE_ATTRIBUTES.detect(),
            metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
        )
    )

    logging.basicConfig(level=logging.DEBUG)
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
