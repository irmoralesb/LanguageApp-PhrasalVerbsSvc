from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import timedelta
from typing import Any, Optional
import os
import uuid

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Pydantic v2 will automatically:
    - Read from environment variables matching field names (case-insensitive by default)
    - Validate types and constraints
    - Raise validation errors if required settings are missing or invalid
    """
    
    # Auth Configuration (for verifying JWT tokens from the Identity Service)
    secret_token_key: str = Field(
        description="Secret key for JWT token verification. Must match the Identity Service.",
        min_length=32,
    )
    auth_algorithm: str = Field(
        min_length=3,
        description="JWT algorithm to use (e.g., HS256, RS256)",
    )
    token_time_delta_in_minutes: int = Field(
        description="Token expiration time in minutes. Must be positive.",
        gt=0,
    )
    
    # Database Configuration
    # Standard env: DATABASE_URL / DATABASE_MIGRATION_URL.
    # Azure Connection strings are exposed as SQLCONNSTR_*, SQLAZURECONNSTR_*, CUSTOMCONNSTR_*.
    database_url: str = Field(
        description="Database connection URL for application runtime (async driver)",
    )
    database_migration_url: str = Field(
        description="Database connection URL for migrations (sync driver)",
    )
    
    @model_validator(mode="before")
    @classmethod
    def read_azure_connection_strings(cls, data: Any) -> Any:
        """Inject database URLs from Azure App Service connection string env vars when standard names are missing."""
        if not isinstance(data, dict):
            return data
        out = dict(data)
        prefixes = ("SQLCONNSTR_", "SQLAZURECONNSTR_", "CUSTOMCONNSTR_")
        for field_name, env_bases in (
            ("database_url", ("DATABASE_URL", "DatabaseUrl")),
            ("database_migration_url", ("DATABASE_MIGRATION_URL", "DatabaseMigrationUrl")),
        ):
            if out.get(field_name):
                continue
            for prefix in prefixes:
                for base in env_bases:
                    val = os.environ.get(prefix + base)
                    if val:
                        out[field_name] = val
                        break
                if out.get(field_name):
                    break
        return out
    
    # CORS Configuration
    cors_allow_origins: str = Field(
        default="*",
        description="CORS allowed origins (comma-separated or *)",
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Application log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    
    # Azure Monitor / Application Insights Configuration
    applicationinsights_connection_string: Optional[str] = Field(
        default=None,
        description="Application Insights connection string for Azure Monitor (logs, traces, metrics)",
    )
    azure_logging_enabled: bool = Field(
        default=True,
        description="Send logs to Azure Monitor when connection string is set",
    )
    azure_tracing_enabled: bool = Field(
        default=True,
        description="Send traces to Azure Monitor when connection string is set",
    )
    azure_metrics_enabled: bool = Field(
        default=True,
        description="Send custom metrics to Azure Monitor when connection string is set",
    )
    structured_logging_enabled: bool = Field(
        default=True,
        description="Enable structured JSON logging with rich context",
    )
    min_log_level_for_azure: str = Field(
        default="INFO",
        description="Minimum log level to send to Azure (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    azure_log_batch_delay_millis: int = Field(
        default=60000,
        description="Azure log batch export delay in milliseconds",
        gt=0,
    )
    metrics_collection_interval: int = Field(
        default=60,
        description="Metrics export interval in seconds",
        gt=0,
    )
    token_url: str = Field(
        description="This is the token URL, for instance /token"
    )

    # Tracing Configuration (Azure Monitor)
    trace_sample_rate: float = Field(
        default=1.0,
        description="Trace sampling rate (0.0 to 1.0, where 1.0 means 100%)",
        ge=0.0,
        le=1.0,
    )
    enable_trace_console_export: bool = Field(
        default=False,
        description="Enable console export of traces for debugging",
    )

    # Service Configuration
    service_id: uuid.UUID = Field(
        description="Id of this microservice for RBAC scoping and tracing"
    )
    service_name: str = Field(
        min_length=1,
        description="Name of this microservice (must match Identity Service registration, used for role lookup in JWT claims)",
    )
    
    model_config = SettingsConfigDict(
        # No env_file: config comes only from environment variables, so .env is not required (e.g. Azure, Docker).
        # For local dev, call load_dotenv() in the app entrypoint (main.py) before importing settings.
        case_sensitive=False,
        extra="ignore",
    )
    
    @field_validator("token_time_delta_in_minutes", mode="before")
    @classmethod
    def validate_token_delta_not_default(cls, v):
        if v == "0" or v == 0:
            raise ValueError("token_time_delta_in_minutes must be greater than 0")
        return v
    
    @property
    def token_expiry_delta(self) -> timedelta:
        return timedelta(minutes=self.token_time_delta_in_minutes)


app_settings: Settings = Settings() # type: ignore
