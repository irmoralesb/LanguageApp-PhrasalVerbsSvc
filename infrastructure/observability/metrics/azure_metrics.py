"""
Centralized Azure Monitor (Application Insights) metrics via OpenTelemetry.

MeterProvider must be initialized by calling init_azure_metrics(connection_string) at startup.
Extend this module with domain-specific metrics as needed for your service.
"""

import logging

logger = logging.getLogger(__name__)

_meter = None
_updown_database_connections = None
_counter_database_operations = None
_histogram_database_operation_duration = None
_counter_application_errors = None
_counter_security_events = None


def init_azure_metrics(
    connection_string: str,
    service_name: str = "service",
    export_interval_seconds: int = 60,
) -> None:
    """
    Initialize Azure Monitor metrics: set MeterProvider and create all instruments.
    Call once at application startup when Azure metrics are enabled.
    """
    global _meter
    global _updown_database_connections, _counter_database_operations, _histogram_database_operation_duration
    global _counter_application_errors, _counter_security_events

    try:
        from opentelemetry import metrics
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter

        exporter = AzureMonitorMetricExporter.from_connection_string(connection_string)
        reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=export_interval_seconds * 1000,
        )
        provider = MeterProvider(metric_readers=[reader])
        metrics.set_meter_provider(provider)
        _meter = provider.get_meter(service_name, "1.0.0")

        _updown_database_connections = _meter.create_up_down_counter(
            "database_connections_active",
            unit="1",
            description="Number of active database connections",
        )
        _counter_database_operations = _meter.create_counter(
            "database_operations_total",
            unit="1",
            description="Total number of database operations",
        )
        _histogram_database_operation_duration = _meter.create_histogram(
            "database_operation_duration_seconds",
            unit="s",
            description="Duration of database operations",
        )
        _counter_application_errors = _meter.create_counter(
            "application_errors_total",
            unit="1",
            description="Total number of application errors",
        )
        _counter_security_events = _meter.create_counter(
            "security_events_total",
            unit="1",
            description="Total number of security events",
        )
        logger.info("Azure Monitor metrics initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Azure metrics: {e}", exc_info=True)
        raise


def _attrs(**kwargs: str) -> dict[str, str]:
    return {k: str(v) for k, v in kwargs.items() if v is not None}


def record_database_metrics(
    operation_type: str,
    table: str,
    duration: float,
    status: str = "success",
) -> None:
    try:
        if _counter_database_operations is None:
            return
        _counter_database_operations.add(
            1, _attrs(operation_type=operation_type, table=table, status=status)
        )
        _histogram_database_operation_duration.record(
            duration, _attrs(operation_type=operation_type, table=table)
        )
    except Exception as e:
        logger.error(f"Error recording database metrics: {e}")


def database_connections_activating() -> None:
    try:
        if _updown_database_connections is not None:
            _updown_database_connections.add(1)
    except Exception as e:
        logger.error(f"Error recording database connection activation: {e}")


def database_connections_deactivating() -> None:
    try:
        if _updown_database_connections is not None:
            _updown_database_connections.add(-1)
    except Exception as e:
        logger.error(f"Error recording database connection deactivation: {e}")


def record_security_event(event_type: str, severity: str) -> None:
    try:
        if _counter_security_events is not None:
            _counter_security_events.add(1, _attrs(event_type=event_type, severity=severity))
    except Exception as e:
        logger.error(f"Error recording security event metrics: {e}")


def record_application_error(error_type: str, module: str) -> None:
    try:
        if _counter_application_errors is not None:
            _counter_application_errors.add(1, _attrs(error_type=error_type, module=module))
    except Exception as e:
        logger.error(f"Error recording application error metrics: {e}")
