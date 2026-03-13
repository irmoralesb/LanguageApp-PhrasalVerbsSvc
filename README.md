# LanguageApp-PhrasalVerbs

LanguageApp Phrasal Verbs API – English phrasal verbs microservice. Built with FastAPI, SQLAlchemy, and the same infrastructure patterns (database, observability, repository, JWT auth) as the LanguageApp backend.

## CI/CD and Docker

Docker images are built and pushed to **Docker Hub** by GitHub Actions when you push a **tag**. The environment (Prod vs Test) is determined by **which branch contains the tag's commit**:

- **Tag's commit on `main`** → **Prod** image is built and pushed (image tag + `latest`).
- **Tag's commit on `test`** → **Test** image is built and pushed (image tag only).
- If the commit is on both branches, **Prod** is used (main takes precedence). If on neither, the workflow is skipped.

### GitHub secrets (required)

In the repo **Settings → Secrets and variables → Actions**, add:

- **`DOCKERHUB_USERNAME`** – your Docker Hub username.
- **`DOCKERHUB_TOKEN`** – a Docker Hub access token (Account → Security → New Access Token, Read & Write).

### Docker Hub and workflow config

- Create a repository on Docker Hub (e.g. `languageapp-phrasal-verbs`). The workflow uses the repo name set in [.github/workflows/build-and-push-docker.yml](.github/workflows/build-and-push-docker.yml) (`DOCKER_IMAGE_REPO`); change it if your repo name differs.
- After a tag push, the image is available as `$DOCKERHUB_USERNAME/$DOCKER_IMAGE_REPO:<tag>` (and `:latest` for Prod).

### Azure Web Apps

- **Prod:** Use image `youruser/languageapp-phrasal-verbs:latest` or a specific tag (e.g. `:v1.0.0`).
- **Test:** Use image `youruser/languageapp-phrasal-verbs:<test-tag>` (e.g. a tag pushed from the `test` branch).

See **Environment Setup** and **Docker** below for required env vars and run instructions.

## Project Structure

```
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Production Docker image (Python 3.12 + ODBC)
├── alembic.ini                    # Alembic migration configuration
├── .env_template                  # Environment variable template
│
├── alembic/                       # Database migrations
│   ├── env.py
│   └── versions/
│
├── core/                          # Cross-cutting concerns
│   ├── settings.py                # Pydantic BaseSettings (env vars, validation)
│   └── security.py                # Password hashing utilities (bcrypt)
│
├── domain/                        # Domain layer (no infrastructure dependencies)
│   ├── entities/                  # Domain models (dataclasses)
│   ├── exceptions/                # Domain-specific exceptions
│   └── interfaces/                # Repository interfaces (ABC)
│
├── application/                   # Application layer
│   ├── routers/                   # FastAPI routers + dependency injection
│   ├── schemas/                   # Pydantic request/response schemas
│   └── services/                  # Application services (use cases)
│
└── infrastructure/                # Infrastructure layer
    ├── databases/                 # Async SQLAlchemy engine, ORM models
    ├── repositories/              # Repository implementations
    └── observability/             # Azure Monitor: logging, tracing, metrics
```

## Getting Started

### 1. Service registration

Set `SERVICE_NAME` and `SERVICE_ID` in your environment to match your service registration in the LanguageApp Identity Service (e.g. `phrasal-verbs`).

### 2. Environment Setup

Copy `.env_template` to `.env` and fill in the values:

```bash
cp .env_template .env
```

**Required environment variables:**

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async SQLAlchemy URL for runtime (aioodbc) |
| `DATABASE_MIGRATION_URL` | Sync SQLAlchemy URL for Alembic migrations (pyodbc) |
| `SECRET_TOKEN_KEY` | Shared secret for JWT token verification (min 32 chars) |
| `AUTH_ALGORITHM` | JWT algorithm (e.g., `HS256`) |
| `TOKEN_TIME_DELTA_IN_MINUTES` | Token expiration in minutes |
| `TOKEN_URL` | Token endpoint path (e.g., `/token`) |
| `SERVICE_ID` | UUID of this service (for RBAC scoping) |
| `SERVICE_NAME` | Name of this service (must match Identity Service registration) |

**Optional (Azure Monitor):**

| Variable | Description |
|---|---|
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Application Insights connection string |
| `AZURE_LOGGING_ENABLED` | Send logs to Azure Monitor (default: `true`) |
| `AZURE_TRACING_ENABLED` | Send traces to Azure Monitor (default: `true`) |
| `AZURE_METRICS_ENABLED` | Send metrics to Azure Monitor (default: `true`) |

### 3. Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head
```

### 4. Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5. Docker

```bash
docker build -t my-service:latest .
docker run -p 8000:80 --env-file .env my-service:latest
```

## Architecture

This template follows a layered architecture with clear separation of concerns:

- **Domain Layer**: Pure business logic with no infrastructure dependencies. Contains entities (dataclasses), repository interfaces (ABCs), and domain exceptions.
- **Application Layer**: Orchestrates use cases. Contains routers (FastAPI endpoints), services (business workflows), schemas (Pydantic models), and dependency injection wiring.
- **Infrastructure Layer**: Technical implementations. Contains database engine/ORM models, repository implementations (SQLAlchemy), and observability (Azure Monitor).
- **Core**: Cross-cutting utilities shared across layers (settings, security).

## Authentication & Authorization

This template consumes JWT tokens issued by the **Identity Service**. It does not create tokens.

- Tokens are decoded from the `Authorization: Bearer <token>` header.
- User identity and roles are extracted from JWT claims (no database lookup required).
- Role-based access control is enforced via the `require_role("role_name")` dependency.

```python
from application.routers.dependency_utils import require_role, CurrentUserDep

@router.get("", dependencies=[Depends(require_role("admin"))])
async def admin_only_endpoint(current_user: CurrentUserDep):
    ...
```

## Health Check

`GET /health` returns `{"status": "ok"}` for load balancer probes.

## License

MIT License - see [LICENSE](LICENSE) for details.
