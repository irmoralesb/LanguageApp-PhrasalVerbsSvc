from abc import ABC, abstractmethod
from uuid import UUID
from domain.entities.item_model import ItemModel


class ItemRepositoryInterface(ABC):
    """Abstract interface for item persistence operations."""

    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> ItemModel | None:
        ...

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ItemModel]:
        ...

    @abstractmethod
    async def create(self, item: ItemModel) -> ItemModel:
        ...

    @abstractmethod
    async def update(self, item: ItemModel) -> ItemModel | None:
        ...

    @abstractmethod
    async def delete(self, item_id: UUID) -> bool:
        ...
