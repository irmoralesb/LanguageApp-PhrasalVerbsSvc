"""
Decorator functions for automatic metrics instrumentation.
These decorators provide a clean, DRY approach to metrics collection.
"""
from functools import wraps
import time
from typing import Callable, Any
from infrastructure.observability.metrics.azure_metrics import (
    record_database_metrics,
    record_security_event,
)


def track_database_operation(operation_type: str, table: str):
    """
    Decorator to track database operations.
    
    Args:
        operation_type: Type of operation ('insert', 'update', 'select', 'delete')
        table: Table name

    Example:
        >>> @track_database_operation(operation_type='insert', table='items')
        ... async def create_item(item: ItemModel) -> ItemModel:
        ...     # implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.perf_counter() - start_time
                record_database_metrics(
                    operation_type=operation_type,
                    table=table,
                    duration=duration,
                    status='success'
                )
                return result
            except Exception:
                duration = time.perf_counter() - start_time
                record_database_metrics(
                    operation_type=operation_type,
                    table=table,
                    duration=duration,
                    status='error'
                )
                raise
        
        return wrapper
    return decorator


def track_security_event(event_type: str, severity: str):
    """
    Decorator to record security events after successful execution.
    
    Args:
        event_type: Type of security event ('unauthorized_access', etc.)
        severity: Event severity ('low', 'medium', 'high', 'critical')

    Example:
        >>> @track_security_event(event_type='unauthorized_access', severity='medium')
        ... async def restricted_action() -> bool:
        ...     # implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            result = await func(*args, **kwargs)
            
            if result:
                record_security_event(
                    event_type=event_type,
                    severity=severity
                )
            
            return result
        
        return wrapper
    return decorator
