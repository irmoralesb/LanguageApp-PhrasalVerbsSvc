import datetime
import uuid

from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER, DATETIME2

from infrastructure.databases.database import Base


class ItemDataModel(Base):
    """Sample ORM model demonstrating the data model pattern."""
    __tablename__ = "items"

    id: Mapped[uuid.UUID] = mapped_column(
        UNIQUEIDENTIFIER(as_uuid=True),
        default=uuid.uuid4,
        primary_key=True, index=False)
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(
        String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DATETIME2(precision=6), server_default=func.sysutcdatetime(), nullable=False)

