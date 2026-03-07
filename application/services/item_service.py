from uuid import UUID

from domain.entities.item_model import ItemModel
from domain.exceptions.item_errors import ItemNotFoundError
from domain.interfaces.item_repository import ItemRepositoryInterface


class ItemService:
    """Sample application service demonstrating the service pattern with CRUD operations."""

    def __init__(self, item_repo: ItemRepositoryInterface):
        self.item_repo = item_repo

    async def get_by_id(self, item_id: UUID) -> ItemModel:
        item = await self.item_repo.get_by_id(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ItemModel]:
        return await self.item_repo.get_all(skip=skip, limit=limit)

    async def create(self, item: ItemModel) -> ItemModel:
        return await self.item_repo.create(item)

    async def update(self, item_id: UUID, name: str, description: str | None, is_active: bool) -> ItemModel:
        existing = await self.item_repo.get_by_id(item_id)
        if existing is None:
            raise ItemNotFoundError(item_id)

        existing.name = name
        existing.description = description
        existing.is_active = is_active

        updated = await self.item_repo.update(existing)
        if updated is None:
            raise ItemNotFoundError(item_id)
        return updated

    async def delete(self, item_id: UUID) -> bool:
        existing = await self.item_repo.get_by_id(item_id)
        if existing is None:
            raise ItemNotFoundError(item_id)
        return await self.item_repo.delete(item_id)
