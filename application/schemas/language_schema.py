from uuid import UUID
from pydantic import BaseModel


class LanguageResponse(BaseModel):
    id: UUID
    code: str
    name: str
    is_target_language: bool
    is_native_language: bool

    model_config = {"from_attributes": True}
