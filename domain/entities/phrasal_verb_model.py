from dataclasses import dataclass
from uuid import UUID
import datetime


@dataclass
class PhrasalVerbModel:
    id: UUID | None
    verb: str
    particle: str
    definition: str
    example_sentence: str | None = None
    is_catalog: bool = True
    created_by_user_id: UUID | None = None
    created_at: datetime.datetime | None = None
