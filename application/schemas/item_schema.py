from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ItemCreate(BaseModel):
    """Schema for creating a new item."""
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class ItemResponse(BaseModel):
    """Schema for item responses."""
    id: UUID
    name: str
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
