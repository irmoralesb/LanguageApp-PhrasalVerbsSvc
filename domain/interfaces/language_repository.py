from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.language_model import LanguageModel


class LanguageRepositoryInterface(ABC):

    @abstractmethod
    async def get_all(self) -> list[LanguageModel]:
        ...

    @abstractmethod
    async def get_by_id(self, language_id: UUID) -> LanguageModel | None:
        ...

    @abstractmethod
    async def get_target_languages(self) -> list[LanguageModel]:
        ...

    @abstractmethod
    async def get_native_languages(self) -> list[LanguageModel]:
        ...
