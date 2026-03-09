"""
Centralized security activity logger for the Phrasal Verbs service.

Combines structured logging (Azure Monitor) and metrics recording for
authentication, authorization, and access-denial events. Designed to be
called directly from the auth/role-check dependencies.
"""

import logging
from uuid import UUID

from infrastructure.observability.logging.azure_handler import (
    get_structured_logger,
    log_security_event,
    log_authorization_check,
)
from infrastructure.observability.metrics.azure_metrics import record_security_event

logger = get_structured_logger("security")


def log_authentication_success(user_id: UUID, email: str) -> None:
    log_security_event(
        logger=logger,
        event_type="authentication_success",
        severity="low",
        user_id=user_id,
        details={"email": email, "action": "token_decoded"},
    )
    record_security_event(event_type="authentication_success", severity="low")


def log_authentication_failure(detail: str) -> None:
    log_security_event(
        logger=logger,
        event_type="authentication_failure",
        severity="medium",
        details={"action": "token_decode_failed", "detail": detail},
    )
    record_security_event(event_type="authentication_failure", severity="medium")


def log_role_check_granted(user_id: UUID, role: str, resource: str | None = None) -> None:
    log_authorization_check(
        logger=logger,
        user_id=user_id,
        required_roles=[role],
        user_roles=[role],
        is_authorized=True,
        resource=resource,
    )
    record_security_event(event_type="role_check_granted", severity="low")


def log_role_check_denied(user_id: UUID, role: str, resource: str | None = None) -> None:
    log_authorization_check(
        logger=logger,
        user_id=user_id,
        required_roles=[role],
        user_roles=[],
        is_authorized=False,
        resource=resource,
    )
    record_security_event(event_type="role_check_denied", severity="medium")
