import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.phrasal_verb_model import PhrasalVerbModel
from domain.interfaces.phrasal_verb_repository import PhrasalVerbRepositoryInterface
from infrastructure.databases.models import PhrasalVerbDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class PhrasalVerbRepository(PhrasalVerbRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='read', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='select', table='phrasal_verbs')
    @track_database_operation(operation_type='select', table='phrasal_verbs')
    async def get_by_id(self, phrasal_verb_id: UUID) -> PhrasalVerbModel | None:
        result = await self.db.execute(
            select(PhrasalVerbDataModel).where(PhrasalVerbDataModel.id == phrasal_verb_id)
        )
        row = result.scalars().first()
        return self._to_domain(row) if row else None

    @log_database_operation_decorator(operation_type='query', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='select', table='phrasal_verbs')
    @track_database_operation(operation_type='select', table='phrasal_verbs')
    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PhrasalVerbModel]:
        result = await self.db.execute(
            select(PhrasalVerbDataModel)
            .where(PhrasalVerbDataModel.is_catalog.is_(True))
            .order_by(PhrasalVerbDataModel.verb, PhrasalVerbDataModel.particle)
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='select', table='phrasal_verbs')
    @track_database_operation(operation_type='select', table='phrasal_verbs')
    async def get_by_user(self, user_id: UUID) -> list[PhrasalVerbModel]:
        result = await self.db.execute(
            select(PhrasalVerbDataModel)
            .where(
                PhrasalVerbDataModel.is_catalog.is_(False),
                PhrasalVerbDataModel.created_by_user_id == user_id,
            )
            .order_by(PhrasalVerbDataModel.verb)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='create', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='insert', table='phrasal_verbs')
    @track_database_operation(operation_type='insert', table='phrasal_verbs')
    async def create(self, phrasal_verb: PhrasalVerbModel) -> PhrasalVerbModel:
        db_item = PhrasalVerbDataModel(
            id=phrasal_verb.id or uuid.uuid4(),
            verb=phrasal_verb.verb,
            particle=phrasal_verb.particle,
            definition=phrasal_verb.definition,
            example_sentence=phrasal_verb.example_sentence,
            is_catalog=phrasal_verb.is_catalog,
            created_by_user_id=phrasal_verb.created_by_user_id,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='update', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='update', table='phrasal_verbs')
    @track_database_operation(operation_type='update', table='phrasal_verbs')
    async def update(self, phrasal_verb: PhrasalVerbModel) -> PhrasalVerbModel | None:
        result = await self.db.execute(
            select(PhrasalVerbDataModel).where(PhrasalVerbDataModel.id == phrasal_verb.id)
        )
        db_item = result.scalars().first()
        if db_item is None:
            return None

        db_item.verb = phrasal_verb.verb
        db_item.particle = phrasal_verb.particle
        db_item.definition = phrasal_verb.definition
        db_item.example_sentence = phrasal_verb.example_sentence

        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='delete', entity_type='phrasal_verb')
    @trace_database_operation(operation_type='delete', table='phrasal_verbs')
    @track_database_operation(operation_type='delete', table='phrasal_verbs')
    async def delete(self, phrasal_verb_id: UUID) -> bool:
        result = await self.db.execute(
            delete(PhrasalVerbDataModel).where(PhrasalVerbDataModel.id == phrasal_verb_id)
        )
        return result.rowcount > 0

    @staticmethod
    def _to_domain(row: PhrasalVerbDataModel) -> PhrasalVerbModel:
        return PhrasalVerbModel(
            id=row.id,
            verb=row.verb,
            particle=row.particle,
            definition=row.definition,
            example_sentence=row.example_sentence,
            is_catalog=row.is_catalog,
            created_by_user_id=row.created_by_user_id,
            created_at=row.created_at,
        )
