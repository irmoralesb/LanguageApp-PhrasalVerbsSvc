from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from core.settings import app_settings
import logging
import os

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from domain.exceptions.auth_errors import (
    MissingPermissionError,
    MissingRoleError,
    UnauthorizedUserError,
)
from domain.exceptions.item_errors import ItemNotFoundError, ItemAlreadyExistsError
from application.routers import item_router
from infrastructure.observability.logging.azure_handler import (
    setup_azure_handler,
    get_structured_logger,
)
from infrastructure.observability.tracing.azure_tracing import setup_azure_tracer
from infrastructure.observability.metrics.azure_metrics import init_azure_metrics
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

LOG_LEVEL = app_settings.log_level
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verbose startup: log config and verify database connection."""
    logger.info("=" * 60)
    logger.info("%s starting (verbose startup)", app_settings.service_name)
    logger.info("=" * 60)

    port = os.environ.get("WEBSITES_PORT") or os.environ.get("PORT") or "80"
    logger.info("[Startup] Port (WEBSITES_PORT/PORT): %s", port)
    logger.info("[Startup] Log level: %s", app_settings.log_level)
    cors_preview = app_settings.cors_allow_origins[:80] + ("..." if len(app_settings.cors_allow_origins) > 80 else "")
    logger.info("[Startup] CORS origins: %s", cors_preview)
    logger.info("[Startup] Service ID: %s", app_settings.service_id)
    logger.info("[Startup] Service Name: %s", app_settings.service_name)
    azure_cs = app_settings.applicationinsights_connection_string
    logger.info("[Startup] Observability - Azure Monitor: %s (logging: %s, tracing: %s, metrics: %s)",
                "enabled" if azure_cs else "disabled",
                "enabled" if (azure_cs and app_settings.azure_logging_enabled) else "disabled",
                "enabled" if (azure_cs and app_settings.azure_tracing_enabled) else "disabled",
                "enabled" if (azure_cs and app_settings.azure_metrics_enabled) else "disabled")

    try:
        from urllib.parse import urlparse
        parsed = urlparse(app_settings.database_url)
        db_display = f"{parsed.scheme}://{parsed.hostname or '(unknown)'}:{parsed.port or '(default)'}/..."
        logger.info("[Startup] Database URL (masked): %s", db_display)
    except Exception as e:
        logger.warning("[Startup] Could not parse database URL for log: %s", e)

    logger.info("[Startup] Testing database connection...")
    try:
        from sqlalchemy import text
        from infrastructure.databases.database import engine
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("[Startup] Database connection: OK")
    except Exception as e:
        logger.error("[Startup] Database connection: FAILED - %s", e, exc_info=True)
        raise

    logger.info("[Startup] All startup checks passed. Ready to accept requests.")
    logger.info("=" * 60)

    yield

    logger.info("%s shutting down.", app_settings.service_name)


app = FastAPI(
    title=app_settings.service_name,
    description="LanguageApp Phrasal Verbs API – English phrasal verbs service",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
cors_origins = app_settings.cors_allow_origins
origins = [origin.strip()
           for origin in cors_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MissingPermissionError)
async def permission_exception_handler(request, exc: MissingPermissionError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": f"Permission denied: {str(exc)}",
            "resource": exc.resource,
            "action": exc.action
        }
    )


@app.exception_handler(MissingRoleError)
async def role_exception_handler(request, exc: MissingRoleError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "detail": f"Role required: {str(exc)}",
            "role": exc.role_name
        }
    )


@app.exception_handler(UnauthorizedUserError)
async def unauthorized_exception_handler(request, exc: UnauthorizedUserError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc)}
    )


@app.exception_handler(ItemNotFoundError)
async def item_not_found_exception_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(ItemAlreadyExistsError)
async def item_already_exists_exception_handler(request, exc: ItemAlreadyExistsError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc)}
    )


# Azure Monitor observability (Application Insights)
AZURE_CS = app_settings.applicationinsights_connection_string

if AZURE_CS:
    if app_settings.azure_logging_enabled:
        try:
            azure_handler = setup_azure_handler(
                connection_string=AZURE_CS,
                log_level=app_settings.min_log_level_for_azure,
                batch_delay_millis=app_settings.azure_log_batch_delay_millis,
            )
            root_logger = logging.getLogger()
            root_logger.addHandler(azure_handler)
            logger.info("Azure Monitor logging enabled")
            startup_logger = get_structured_logger("startup")
            startup_logger.info(
                "%s started",
                app_settings.service_name,
                extra={
                    "event_type": "application_startup",
                    "service_id": str(app_settings.service_id),
                    "service_name": app_settings.service_name,
                    "log_level": LOG_LEVEL,
                    "azure_logging_enabled": True,
                },
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure logging: {e}", exc_info=True)
    else:
        logger.info("Azure logging disabled")

    if app_settings.azure_tracing_enabled:
        try:
            setup_azure_tracer(
                connection_string=AZURE_CS,
                service_name=app_settings.service_name,
                sample_rate=app_settings.trace_sample_rate,
                enable_console_export=app_settings.enable_trace_console_export,
            )
            FastAPIInstrumentor.instrument_app(app)
            from infrastructure.databases.database import engine
            SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
            logger.info(
                f"Azure tracing enabled (sample_rate={app_settings.trace_sample_rate})"
            )
            startup_logger = get_structured_logger("startup")
            startup_logger.info(
                "Distributed tracing initialized",
                extra={
                    "event_type": "tracing_startup",
                    "service_name": app_settings.service_name,
                    "sample_rate": app_settings.trace_sample_rate,
                },
            )
        except Exception as e:
            logger.error(f"Failed to initialize Azure tracing: {e}", exc_info=True)
    else:
        logger.info("Azure tracing disabled")

    if app_settings.azure_metrics_enabled:
        try:
            init_azure_metrics(
                connection_string=AZURE_CS,
                service_name=app_settings.service_name,
                export_interval_seconds=app_settings.metrics_collection_interval,
            )
            logger.info("Azure Monitor metrics enabled")
        except Exception as e:
            logger.error(f"Failed to initialize Azure metrics: {e}", exc_info=True)
    else:
        logger.info("Azure metrics disabled")
else:
    logger.info("Azure Monitor observability disabled (no connection string)")


app.include_router(item_router.router)


@app.get("/")
async def root():
    return {"message": f"Welcome to {app_settings.service_name}"}


@app.get("/health")
async def health():
    """Health check endpoint for Azure App Service and load balancer probes."""
    return {"status": "ok"}
