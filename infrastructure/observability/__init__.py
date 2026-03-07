# Observability subpackage structure:
# observability/
# ├── __init__.py
# ├── metrics/
# │   ├── azure_metrics.py      # Azure Monitor metrics setup and record_* helpers
# │   └── decorators.py         # Metric collection decorators
# ├── logging/
# │   ├── azure_handler.py      # Azure Monitor logging handler and structured helpers
# │   └── decorators.py         # Logging decorators
# └── tracing/
#     ├── azure_tracing.py      # Tracer setup and span enrichment
#     └── decorators.py         # Tracing decorators
