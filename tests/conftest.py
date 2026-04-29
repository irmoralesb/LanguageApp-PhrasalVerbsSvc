"""
Ensure required environment variables exist before ``core.settings`` is imported.

``app_settings`` is instantiated at import time in ``core.settings``.
"""
import os
import uuid

_DEFAULTS = {
    "SECRET_TOKEN_KEY": "x" * 40,
    "AUTH_ALGORITHM": "HS256",
    "TOKEN_TIME_DELTA_IN_MINUTES": "60",
    "DATABASE_URL": "mssql+pyodbc://user:pass@localhost/testdb",
    "DATABASE_MIGRATION_URL": "mssql+pyodbc://user:pass@localhost/testdbadm",
    "TOKEN_URL": "/token",
    "SERVICE_NAME": "phrasal-verbs-tests",
}


def pytest_configure():
    srv = str(uuid.UUID(int=123))
    os.environ.setdefault("SERVICE_ID", srv)
    for key, val in _DEFAULTS.items():
        os.environ.setdefault(key, val)
