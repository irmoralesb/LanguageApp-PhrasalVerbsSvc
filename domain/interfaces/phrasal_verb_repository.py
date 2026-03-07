from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.phrasal_verb_model import PhrasalVerbModel


class PhrasalVerbRepositoryInterface(ABC):

    @abstractmethod
    async def get_by_id(self, phrasal_verb_id: UUID) -> PhrasalVerbModel | None:
        ...

    @abstractmethod
    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PhrasalVerbModel]:
        ...

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> list[PhrasalVerbModel]:
        ...

    @abstractmethod
    async def create(self, phrasal_verb: PhrasalVerbModel) -> PhrasalVerbModel:
        ...

    @abstractmethod
    async def update(self, phrasal_verb: PhrasalVerbModel) -> PhrasalVerbModel | None:
        ...

    @abstractmethod
    async def delete(self, phrasal_verb_id: UUID) -> bool:
        ...
