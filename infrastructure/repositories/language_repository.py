from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.language_model import LanguageModel
from domain.interfaces.language_repository import LanguageRepositoryInterface
from infrastructure.databases.models import LanguageDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class LanguageRepository(LanguageRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='query', entity_type='language')
    @trace_database_operation(operation_type='select', table='languages')
    @track_database_operation(operation_type='select', table='languages')
    async def get_all(self) -> list[LanguageModel]:
        result = await self.db.execute(
            select(LanguageDataModel).order_by(LanguageDataModel.name)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='read', entity_type='language')
    @trace_database_operation(operation_type='select', table='languages')
    @track_database_operation(operation_type='select', table='languages')
    async def get_by_id(self, language_id: UUID) -> LanguageModel | None:
        result = await self.db.execute(
            select(LanguageDataModel).where(LanguageDataModel.id == language_id)
        )
        row = result.scalars().first()
        return self._to_domain(row) if row else None

    @log_database_operation_decorator(operation_type='query', entity_type='language')
    @trace_database_operation(operation_type='select', table='languages')
    @track_database_operation(operation_type='select', table='languages')
    async def get_target_languages(self) -> list[LanguageModel]:
        result = await self.db.execute(
            select(LanguageDataModel)
            .where(LanguageDataModel.is_target_language.is_(True))
            .order_by(LanguageDataModel.name)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='language')
    @trace_database_operation(operation_type='select', table='languages')
    @track_database_operation(operation_type='select', table='languages')
    async def get_native_languages(self) -> list[LanguageModel]:
        result = await self.db.execute(
            select(LanguageDataModel)
            .where(LanguageDataModel.is_native_language.is_(True))
            .order_by(LanguageDataModel.name)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @staticmethod
    def _to_domain(row: LanguageDataModel) -> LanguageModel:
        return LanguageModel(
            id=row.id,
            code=row.code,
            name=row.name,
            is_target_language=row.is_target_language,
            is_native_language=row.is_native_language,
        )
