from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class UserProfileCreate(BaseModel):
    native_language_id: UUID
    learning_language_ids: list[UUID] = Field(default_factory=list)


class UserProfileUpdate(BaseModel):
    native_language_id: UUID


class UserProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    native_language_id: UUID
    learning_language_ids: list[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AddLearningLanguage(BaseModel):
    language_id: UUID


class AddPhrasalVerbSelection(BaseModel):
    phrasal_verb_id: UUID


class PhrasalVerbSelectionResponse(BaseModel):
    id: UUID
    user_id: UUID
    phrasal_verb_id: UUID
    added_at: datetime

    model_config = {"from_attributes": True}
