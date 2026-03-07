from dataclasses import dataclass
from uuid import UUID
import datetime


@dataclass
class ItemModel:
    """Sample domain entity demonstrating the entity pattern."""
    id: UUID | None
    name: str
    description: str | None = None
    is_active: bool = True
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None
