from dataclasses import dataclass, field
from uuid import UUID
import datetime


@dataclass
class UserProfileModel:
    id: UUID | None
    user_id: UUID
    native_language_id: UUID
    learning_language_ids: list[UUID] = field(default_factory=list)
    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = None


@dataclass
class UserPhrasalVerbSelectionModel:
    id: UUID | None
    user_id: UUID
    phrasal_verb_id: UUID
    added_at: datetime.datetime | None = None
