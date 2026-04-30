"""Unit tests for domain.entities.token_claims."""

from uuid import uuid4

from domain.entities.token_claims import UserClaims


def test_user_claims_roles_default_empty() -> None:
    uid = uuid4()
    c = UserClaims(user_id=uid, email="a@b.c")
    assert c.roles == {}


def test_user_claims_stores_roles() -> None:
    uid = uuid4()
    c = UserClaims(
        user_id=uid,
        email="test@test.com",
        roles={"svc": ["a", "b"]},
    )
    assert c.roles["svc"] == ["a", "b"]
