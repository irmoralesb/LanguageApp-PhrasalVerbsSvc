"""Unit tests for PhrasalVerbs TokenService JWT decoding."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest

from application.services.token_service import TokenService


def test_decode_token_extracts_claims() -> None:
    secret = "secret-key-consumer-test-phrasal-verbs-32b"
    uid = uuid4()
    roles = {"phrasal-verbs": ["user"]}
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(uid),
        "email": "u@example.com",
        "roles": roles,
        "exp": now + timedelta(hours=1),
        "iat": now,
    }
    tok = jwt.encode(payload, secret, algorithm="HS256")
    svc = TokenService(secret_key=secret, algorithm="HS256")
    claims = svc.decode_token(tok)
    assert claims.user_id == uid
    assert claims.email == "u@example.com"
    assert claims.roles == roles


def test_decode_token_raises_when_sub_missing() -> None:
    secret = "secret-key-consumer-test-phrasal-verbs-32b"
    now = datetime.now(timezone.utc)
    tok = jwt.encode(
        {"email": "a@b.com", "exp": now + timedelta(hours=1), "iat": now},
        secret,
        algorithm="HS256",
    )
    svc = TokenService(secret_key=secret, algorithm="HS256")
    with pytest.raises(ValueError, match="sub"):
        svc.decode_token(tok)
