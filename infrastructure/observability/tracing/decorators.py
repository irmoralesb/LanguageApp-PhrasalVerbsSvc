"""
Tracing decorators for automatic span creation and instrumentation.

Pattern:
--------
- Factory functions return configured decorators
- All decorators support async functions
- Automatic timing and error recording
- Wrapped in try-except to prevent tracing failures from breaking business logic
"""

import time
from functools import wraps
from typing import Any, Callable
from uuid import UUID

from opentelemetry.trace import Status, StatusCode

from infrastructure.observability.tracing.azure_tracing import (
    get_tracer,
    enrich_database_operation_span,
    enrich_authorization_span,
    enrich_security_event_span,
)


def trace_database_operation(operation_type: str, table: str):
    """
    Decorator to trace database operations.

    Args:
        operation_type: Type of operation ('select', 'insert', 'update', 'delete')
        table: Database table name

    Example:
        >>> @trace_database_operation(operation_type='insert', table='items')
        ... async def create_item_in_db(item: ItemModel) -> ItemModel:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer(func.__module__)
            span_name = f"db.{operation_type}.{table}.{func.__name__}"

            try:
                with tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    start_time = time.perf_counter()

                    try:
                        result = await func(*args, **kwargs)
                        duration = time.perf_counter() - start_time

                        enrich_database_operation_span(
                            span=span,
                            operation_type=operation_type,
                            table=table,
                            status="success",
                            duration_seconds=round(duration, 4),
                        )

                        return result

                    except Exception as e:
                        duration = time.perf_counter() - start_time

                        span.record_exception(e)
                        enrich_database_operation_span(
                            span=span,
                            operation_type=operation_type,
                            table=table,
                            status="failure",
                            duration_seconds=round(duration, 4),
                        )
                        raise

            except Exception:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def trace_authorization(resource: str, action: str):
    """
    Decorator to trace authorization checks.

    Args:
        resource: Resource being accessed
        action: Action being performed

    Example:
        >>> @trace_authorization(resource='item', action='delete')
        ... async def check_delete_permission(user: UserClaims) -> bool:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer(func.__module__)
            span_name = f"authz.{resource}.{action}.{func.__name__}"

            try:
                with tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    start_time = time.perf_counter()

                    user_id = kwargs.get("user_id")
                    user = kwargs.get("user")
                    if not user_id and user:
                        if hasattr(user, "id"):
                            user_id = user.id
                        elif hasattr(user, "user_id"):
                            user_id = user.user_id

                    required_roles = kwargs.get("required_roles", [])
                    user_roles = kwargs.get("user_roles", [])

                    try:
                        result = await func(*args, **kwargs)
                        duration = time.perf_counter() - start_time

                        is_authorized = bool(result)

                        enrich_authorization_span(
                            span=span,
                            resource=resource,
                            action=action,
                            is_authorized=is_authorized,
                            user_id=user_id,
                            required_roles=required_roles,
                            user_roles=user_roles,
                            duration_seconds=round(duration, 4),
                        )

                        return result

                    except Exception as e:
                        duration = time.perf_counter() - start_time

                        span.record_exception(e)
                        enrich_authorization_span(
                            span=span,
                            resource=resource,
                            action=action,
                            is_authorized=False,
                            user_id=user_id,
                            required_roles=required_roles,
                            user_roles=user_roles,
                            duration_seconds=round(duration, 4),
                        )
                        raise

            except Exception:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def trace_security_event(event_type: str, severity: str):
    """
    Decorator to trace security events.

    Args:
        event_type: Type of security event
        severity: Event severity (low, medium, high, critical)

    Example:
        >>> @trace_security_event(event_type='unauthorized_access', severity='medium')
        ... async def restricted_action(user_id: UUID) -> bool:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer(func.__module__)
            span_name = f"security.{event_type}.{func.__name__}"

            try:
                with tracer.start_as_current_span(span_name) as span:
                    span.set_attribute("function.name", func.__name__)
                    span.set_attribute("function.module", func.__module__)

                    start_time = time.perf_counter()

                    user_id = kwargs.get("user_id")
                    if not user_id and len(args) > 1:
                        potential_id = args[1] if len(args) > 1 else None
                        if isinstance(potential_id, UUID):
                            user_id = potential_id

                    try:
                        result = await func(*args, **kwargs)
                        duration = time.perf_counter() - start_time

                        enrich_security_event_span(
                            span=span,
                            event_type=event_type,
                            severity=severity,
                            user_id=user_id,
                            details={"duration_seconds": round(duration, 4)},
                        )

                        return result

                    except Exception as e:
                        duration = time.perf_counter() - start_time

                        span.record_exception(e)
                        enrich_security_event_span(
                            span=span,
                            event_type=event_type,
                            severity=severity,
                            user_id=user_id,
                            details={
                                "duration_seconds": round(duration, 4),
                                "error": type(e).__name__,
                            },
                        )
                        raise

            except Exception:
                return await func(*args, **kwargs)

        return wrapper

    return decorator
