from dataclasses import dataclass
from uuid import UUID


@dataclass
class LanguageModel:
    id: UUID | None
    code: str
    name: str
    is_target_language: bool = False
    is_native_language: bool = False
