# Database Infrastructure

LanguageApp Phrasal Verbs service – FastAPI-based microservice using SQLAlchemy 2.x with async sessions and SQL Server 2022 as the backing store.

## Database drivers

### pyodbc (sync driver, used for migrations)
- Best compatibility with SQL Server features; leveraged by Alembic through `DATABASE_MIGRATION_URL`.
- SQLAlchemy URL example (SQL Server 2022, ODBC Driver 18):

```bash
mssql+pyodbc://<username>:<password>@<host>:1433/<database>?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes&LongAsMax=Yes
```

### aioodbc (async driver, runtime)
- Async DBAPI built on top of pyodbc; use with `create_async_engine` by switching the scheme to `mssql+aioodbc`.
- SQLAlchemy async URL example:

```bash
mssql+aioodbc://<username>:<password>@<host>:1433/<database>?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=yes&timeout=30&LongAsMax=Yes
```

## Current database implementation
- Runtime uses SQLAlchemy async engine with the `DATABASE_URL` URL and automatically injects `LongAsMax=Yes` to preserve `MAX` semantics when pyodbc is the driver (see [database.py](database.py)).
- Engine opts into `pool_pre_ping` and a 30s timeout, and disables `fast_executemany`/`setinputsizes` to avoid driver quirks with SQL Server.
- Sessions are yielded by `get_monitored_db_session`, which tracks connection activation/deactivation metrics and commits when mutations are present.
- Alembic reads `DATABASE_MIGRATION_URL` for migrations, keeping a separate sync-safe URL for schema changes.

## Environment setup
1. Copy `.env_template` to `.env` and fill in the values.
2. Ensure ODBC Driver 18 for SQL Server is installed and reachable from the host/container.

Required variables:

- `DATABASE_URL` -- async SQLAlchemy URL for application traffic (aioodbc).
- `DATABASE_MIGRATION_URL` -- sync SQLAlchemy URL for Alembic migrations (pyodbc).
