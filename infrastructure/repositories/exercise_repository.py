import uuid
from uuid import UUID

from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.exercise_model import ExerciseHistoryRecord, PhrasalVerbStats
from domain.interfaces.exercise_repository import ExerciseRepositoryInterface
from infrastructure.databases.models import ExerciseResultDataModel, PhrasalVerbDataModel
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class ExerciseRepository(ExerciseRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='create', entity_type='exercise_result')
    @trace_database_operation(operation_type='insert', table='exercise_results')
    @track_database_operation(operation_type='insert', table='exercise_results')
    async def save_result(self, record: ExerciseHistoryRecord) -> ExerciseHistoryRecord:
        db_item = ExerciseResultDataModel(
            id=record.id or uuid.uuid4(),
            user_id=record.user_id,
            phrasal_verb_id=record.phrasal_verb_id,
            exercise_type=record.exercise_type,
            target_language_code=record.target_language_code,
            scenario_native=record.scenario_native,
            sentence_native=record.sentence_native,
            sentence_target=record.sentence_target,
            user_answer=record.user_answer,
            is_correct=record.is_correct,
            feedback=record.feedback,
        )
        self.db.add(db_item)
        await self.db.flush()
        await self.db.refresh(db_item)
        return self._to_domain(db_item)

    @log_database_operation_decorator(operation_type='query', entity_type='exercise_result')
    @trace_database_operation(operation_type='select', table='exercise_results')
    @track_database_operation(operation_type='select', table='exercise_results')
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExerciseHistoryRecord]:
        result = await self.db.execute(
            select(ExerciseResultDataModel)
            .where(ExerciseResultDataModel.user_id == user_id)
            .order_by(ExerciseResultDataModel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return [self._to_domain(r) for r in result.scalars().all()]

    @log_database_operation_decorator(operation_type='query', entity_type='exercise_result')
    @trace_database_operation(operation_type='select', table='exercise_results')
    @track_database_operation(operation_type='select', table='exercise_results')
    async def get_stats_by_user(self, user_id: UUID) -> list[PhrasalVerbStats]:
        stmt = (
            select(
                ExerciseResultDataModel.phrasal_verb_id,
                PhrasalVerbDataModel.verb,
                PhrasalVerbDataModel.particle,
                func.sum(case((ExerciseResultDataModel.is_correct.is_(True), 1), else_=0)).label("correct_count"),
                func.sum(case((ExerciseResultDataModel.is_correct.is_(False), 1), else_=0)).label("incorrect_count"),
            )
            .join(PhrasalVerbDataModel, ExerciseResultDataModel.phrasal_verb_id == PhrasalVerbDataModel.id)
            .where(ExerciseResultDataModel.user_id == user_id)
            .group_by(
                ExerciseResultDataModel.phrasal_verb_id,
                PhrasalVerbDataModel.verb,
                PhrasalVerbDataModel.particle,
            )
        )
        result = await self.db.execute(stmt)
        return [
            PhrasalVerbStats(
                phrasal_verb_id=row.phrasal_verb_id,
                verb=row.verb,
                particle=row.particle,
                correct_count=row.correct_count,
                incorrect_count=row.incorrect_count,
            )
            for row in result.all()
        ]

    @staticmethod
    def _to_domain(row: ExerciseResultDataModel) -> ExerciseHistoryRecord:
        return ExerciseHistoryRecord(
            id=row.id,
            user_id=row.user_id,
            phrasal_verb_id=row.phrasal_verb_id,
            exercise_type=row.exercise_type,
            target_language_code=row.target_language_code,
            scenario_native=row.scenario_native,
            sentence_native=row.sentence_native,
            sentence_target=row.sentence_target,
            user_answer=row.user_answer,
            is_correct=row.is_correct,
            feedback=row.feedback,
            created_at=row.created_at,
        )
