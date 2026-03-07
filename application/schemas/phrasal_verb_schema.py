from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class PhrasalVerbCreate(BaseModel):
    verb: str = Field(min_length=1, max_length=100)
    particle: str = Field(min_length=1, max_length=50)
    definition: str = Field(min_length=1, max_length=500)
    example_sentence: str | None = Field(default=None, max_length=1000)


class PhrasalVerbUpdate(BaseModel):
    verb: str = Field(min_length=1, max_length=100)
    particle: str = Field(min_length=1, max_length=50)
    definition: str = Field(min_length=1, max_length=500)
    example_sentence: str | None = Field(default=None, max_length=1000)


class PhrasalVerbResponse(BaseModel):
    id: UUID
    verb: str
    particle: str
    definition: str
    example_sentence: str | None
    is_catalog: bool
    created_by_user_id: UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
