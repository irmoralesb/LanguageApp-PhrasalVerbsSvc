import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.item_model import ItemModel
from domain.interfaces.item_repository import ItemRepositoryInterface
from infrastructure.databases.models import ItemDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class ItemRepository(ItemRepositoryInterface):
    """SQLAlchemy implementation of the item repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='read', entity_type='item')
    @trace_database_operation(operation_type='select', table='items')
    @track_database_operation(operation_type='select', table='items')
    async def get_by_id(self, item_id: UUID) -> ItemModel | None:
        result = await self.db.execute(
            select(ItemDataModel).where(ItemDataModel.id == item_id)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_domain(row)

    @log_database_operation_decorator(operation_type='query', entity_type='item')
    @trace_database_operation(operation_type='select', table='items')
    @track_database_operation(operation_type='select', table='items')
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ItemModel]:
        result = await self.db.execute(
            select(ItemDataModel)
            .offset(skip)
            .limit(limit)
            .order_by(ItemDataModel.created_at.desc())
        )
        rows = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    @log_database_operation_decorator(operation_type='create', entity_type='item')
    @trace_database_operation(operation_type='insert', table='items')
    @track_database_operation(operation_type='insert', table='items')
    async def create(self, item: ItemModel) -> ItemModel:
        db_item = ItemDataModel(
            id=item.id or uuid.uuid4(),
            name=item.name,
            description=item.description,
            is_active=item.is_active,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='update', entity_type='item')
    @trace_database_operation(operation_type='update', table='items')
    @track_database_operation(operation_type='update', table='items')
    async def update(self, item: ItemModel) -> ItemModel | None:
        result = await self.db.execute(
            select(ItemDataModel).where(ItemDataModel.id == item.id)
        )
        db_item = result.scalars().first()
        if db_item is None:
            return None

        db_item.name = item.name
        db_item.description = item.description
        db_item.is_active = item.is_active
        db_item.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='delete', entity_type='item')
    @trace_database_operation(operation_type='delete', table='items')
    @track_database_operation(operation_type='delete', table='items')
    async def delete(self, item_id: UUID) -> bool:
        result = await self.db.execute(
            delete(ItemDataModel).where(ItemDataModel.id == item_id)
        )
        return result.rowcount > 0

    @staticmethod
    def _to_domain(row: ItemDataModel) -> ItemModel:
        return ItemModel(
            id=row.id,
            name=row.name,
            description=row.description,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
