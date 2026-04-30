"""Unit tests for AuthorizationService RBAC helpers."""

from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

import pytest

from application.services.authorization_service import AuthorizationService
from domain.entities.token_claims import UserClaims
from domain.exceptions.auth_errors import MissingRoleError


@pytest.fixture
def user_for_service():
    svc = "phrasal-verbs-tests"
    return UserClaims(
        user_id=uuid4(),
        email="user@test.com",
        roles={svc: ["user", "teacher"]},
    )


def test_check_role_returns_true_when_present(user_for_service):
    with patch(
        "application.services.authorization_service.app_settings",
        SimpleNamespace(service_name="phrasal-verbs-tests"),
    ):
        svc = AuthorizationService()
        assert svc.check_role(user_for_service, "user") is True


def test_check_role_raises_missing(user_for_service):
    with patch(
        "application.services.authorization_service.app_settings",
        SimpleNamespace(service_name="phrasal-verbs-tests"),
    ):
        svc = AuthorizationService()
        with pytest.raises(MissingRoleError) as ei:
            svc.check_role(user_for_service, "admin")
        assert ei.value.role_name == "admin"


def test_get_user_roles_explicit_service(user_for_service):
    svc = AuthorizationService()
    roles = svc.get_user_roles(user_for_service, service_name="phrasal-verbs-tests")
    assert roles == ["user", "teacher"]


def test_check_role_explicit_service_override():
    u = UserClaims(
        user_id=uuid4(),
        email="x@y.z",
        roles={"other-service": ["admin"]},
    )
    svc = AuthorizationService()
    assert svc.check_role(u, "admin", service_name="other-service") is True
