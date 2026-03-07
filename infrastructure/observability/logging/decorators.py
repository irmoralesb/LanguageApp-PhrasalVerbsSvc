"""
Logging decorators for automatic operation instrumentation.

Pattern: Factory functions return decorators with specific configuration.
All decorators support async functions and wrap operations in try-except
blocks to prevent logging failures from breaking business logic.
"""

import time
from functools import wraps
from typing import Any, Callable
from uuid import UUID

from infrastructure.observability.logging.azure_handler import (
    get_structured_logger,
    log_database_operation,
    log_security_event,
    log_authorization_check,
)


def log_operation(operation_type: str, log_level: str = "INFO"):
    """
    Generic decorator to log operation execution with context.

    Args:
        operation_type: Type of operation being performed
        log_level: Log level to use ('DEBUG', 'INFO', 'WARNING', 'ERROR')

    Example:
        >>> @log_operation(operation_type='item_lookup', log_level='DEBUG')
        ... async def find_item_by_id(item_id: UUID) -> Item:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_structured_logger(func.__module__)
            start_time = time.perf_counter()

            logger.log(
                getattr(__import__("logging"), log_level.upper()),
                f"Starting {operation_type}: {func.__name__}",
                extra={
                    "operation_type": operation_type,
                    "function": func.__name__,
                    "module": func.__module__,
                },
            )

            try:
                result = await func(*args, **kwargs)

                duration = time.perf_counter() - start_time
                logger.log(
                    getattr(__import__("logging"), log_level.upper()),
                    f"Completed {operation_type}: {func.__name__}",
                    extra={
                        "operation_type": operation_type,
                        "function": func.__name__,
                        "status": "success",
                        "duration_seconds": round(duration, 4),
                    },
                )

                return result

            except Exception as e:
                duration = time.perf_counter() - start_time
                logger.error(
                    f"Failed {operation_type}: {func.__name__} - {str(e)}",
                    extra={
                        "operation_type": operation_type,
                        "function": func.__name__,
                        "status": "failure",
                        "duration_seconds": round(duration, 4),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


def log_database_operation_decorator(operation_type: str, entity_type: str):
    """
    Decorator to log database operations.

    Args:
        operation_type: Type of operation ('create', 'read', 'update', 'delete', 'query')
        entity_type: Type of entity ('item', etc.)

    Example:
        >>> @log_database_operation_decorator(operation_type='create', entity_type='item')
        ... async def create_item(item: ItemModel) -> ItemModel:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_structured_logger("database")
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)

                duration = time.perf_counter() - start_time

                record_count = None
                if isinstance(result, list):
                    record_count = len(result)
                elif result is not None:
                    record_count = 1

                log_database_operation(
                    logger=logger,
                    operation_type=operation_type,
                    entity_type=entity_type,
                    status="success",
                    duration_seconds=round(duration, 4),
                    record_count=record_count,
                )

                return result

            except Exception as e:
                duration = time.perf_counter() - start_time

                log_database_operation(
                    logger=logger,
                    operation_type=operation_type,
                    entity_type=entity_type,
                    status="failure",
                    duration_seconds=round(duration, 4),
                    error_message=str(e),
                )

                raise

        return wrapper

    return decorator


def log_security_event_decorator(event_type: str, severity: str):
    """
    Decorator to log security events.

    Args:
        event_type: Type of security event ('unauthorized_access', etc.)
        severity: Severity level ('low', 'medium', 'high', 'critical')

    Example:
        >>> @log_security_event_decorator(event_type='unauthorized_access', severity='medium')
        ... async def restricted_action(user_id: UUID) -> bool:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_structured_logger("security")

            user_id = kwargs.get("user_id") or (args[1] if len(args) > 1 and isinstance(args[1], UUID) else None)

            try:
                result = await func(*args, **kwargs)

                log_security_event(
                    logger=logger,
                    event_type=event_type,
                    severity=severity,
                    user_id=user_id,
                    details={"status": "success"},
                )

                return result

            except Exception as e:
                log_security_event(
                    logger=logger,
                    event_type=event_type,
                    severity=severity,
                    user_id=user_id,
                    details={"status": "failure", "error": str(e)},
                )

                raise

        return wrapper

    return decorator


def log_authorization_decorator():
    """
    Decorator to log authorization checks.

    Example:
        >>> @log_authorization_decorator()
        ... async def authorize(user_id: UUID, required_roles: list[str]) -> bool:
        ...     # implementation
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger = get_structured_logger("authorization")
            start_time = time.perf_counter()

            user_id = kwargs.get("user_id")
            required_roles = kwargs.get("required_roles", [])
            resource = kwargs.get("resource")

            try:
                result = await func(*args, **kwargs)

                duration = time.perf_counter() - start_time

                user_roles = kwargs.get("user_roles", [])

                log_authorization_check(
                    logger=logger,
                    user_id=user_id,
                    required_roles=required_roles,
                    user_roles=user_roles,
                    is_authorized=bool(result),
                    resource=resource,
                    duration_seconds=round(duration, 4),
                )

                return result

            except Exception as e:
                duration = time.perf_counter() - start_time

                log_authorization_check(
                    logger=logger,
                    user_id=user_id,
                    required_roles=required_roles,
                    user_roles=[],
                    is_authorized=False,
                    resource=resource,
                    duration_seconds=round(duration, 4),
                )

                raise

        return wrapper

    return decorator
