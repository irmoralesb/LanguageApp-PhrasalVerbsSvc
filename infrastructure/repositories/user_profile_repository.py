import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user_profile_model import UserProfileModel, UserPhrasalVerbSelectionModel
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from infrastructure.databases.models import (
    UserProfileDataModel,
    UserLearningLanguageDataModel,
    UserPhrasalVerbSelectionDataModel,
)
from infrastructure.observability.logging.decorators import log_database_operation_decorator
from infrastructure.observability.tracing.decorators import trace_database_operation
from infrastructure.observability.metrics.decorators import track_database_operation


class UserProfileRepository(UserProfileRepositoryInterface):

    def __init__(self, db: AsyncSession):
        self.db = db

    @log_database_operation_decorator(operation_type='read', entity_type='user_profile')
    @trace_database_operation(operation_type='select', table='user_profiles')
    @track_database_operation(operation_type='select', table='user_profiles')
    async def get_by_user_id(self, user_id: UUID) -> UserProfileModel | None:
        result = await self.db.execute(
            select(UserProfileDataModel).where(UserProfileDataModel.user_id == user_id)
        )
        row = result.scalars().first()
        if row is None:
            return None
        return self._to_domain(row)

    @log_database_operation_decorator(operation_type='create', entity_type='user_profile')
    @trace_database_operation(operation_type='insert', table='user_profiles')
    @track_database_operation(operation_type='insert', table='user_profiles')
    async def create(self, profile: UserProfileModel) -> UserProfileModel:
        db_profile = UserProfileDataModel(
            id=profile.id or uuid.uuid4(),
            user_id=profile.user_id,
            native_language_id=profile.native_language_id,
        )
        self.db.add(db_profile)
        await self.db.flush()

        for lang_id in profile.learning_language_ids:
            ll = UserLearningLanguageDataModel(
                id=uuid.uuid4(),
                user_id=profile.user_id,
                language_id=lang_id,
            )
            self.db.add(ll)

        await self.db.flush()
        await self.db.refresh(db_profile)
        return self._to_domain(db_profile)

    @log_database_operation_decorator(operation_type='update', entity_type='user_profile')
    @trace_database_operation(operation_type='update', table='user_profiles')
    @track_database_operation(operation_type='update', table='user_profiles')
    async def update(self, profile: UserProfileModel) -> UserProfileModel | None:
        result = await self.db.execute(
            select(UserProfileDataModel).where(UserProfileDataModel.user_id == profile.user_id)
        )
        db_profile = result.scalars().first()
        if db_profile is None:
            return None

        db_profile.native_language_id = profile.native_language_id
        db_profile.updated_at = datetime.now(timezone.utc)

        await self.db.flush()
        await self.db.refresh(db_profile)
        return self._to_domain(db_profile)

    @log_database_operation_decorator(operation_type='create', entity_type='user_learning_language')
    @trace_database_operation(operation_type='insert', table='user_learning_languages')
    @track_database_operation(operation_type='insert', table='user_learning_languages')
    async def add_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        ll = UserLearningLanguageDataModel(
            id=uuid.uuid4(),
            user_id=user_id,
            language_id=language_id,
        )
        self.db.add(ll)
        await self.db.flush()

    @log_database_operation_decorator(operation_type='delete', entity_type='user_learning_language')
    @trace_database_operation(operation_type='delete', table='user_learning_languages')
    @track_database_operation(operation_type='delete', table='user_learning_languages')
    async def remove_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        await self.db.execute(
            delete(UserLearningLanguageDataModel).where(
                UserLearningLanguageDataModel.user_id == user_id,
                UserLearningLanguageDataModel.language_id == language_id,
            )
        )

    @log_database_operation_decorator(operation_type='query', entity_type='user_phrasal_verb_selection')
    @trace_database_operation(operation_type='select', table='user_phrasal_verb_selections')
    @track_database_operation(operation_type='select', table='user_phrasal_verb_selections')
    async def get_phrasal_verb_selections(self, user_id: UUID) -> list[UserPhrasalVerbSelectionModel]:
        result = await self.db.execute(
            select(UserPhrasalVerbSelectionDataModel)
            .where(UserPhrasalVerbSelectionDataModel.user_id == user_id)
            .order_by(UserPhrasalVerbSelectionDataModel.added_at.desc())
        )
        return [
            UserPhrasalVerbSelectionModel(
                id=r.id,
                user_id=r.user_id,
                phrasal_verb_id=r.phrasal_verb_id,
                added_at=r.added_at,
            )
            for r in result.scalars().all()
        ]

    @log_database_operation_decorator(operation_type='create', entity_type='user_phrasal_verb_selection')
    @trace_database_operation(operation_type='insert', table='user_phrasal_verb_selections')
    @track_database_operation(operation_type='insert', table='user_phrasal_verb_selections')
    async def add_phrasal_verb_selection(self, user_id: UUID, phrasal_verb_id: UUID) -> UserPhrasalVerbSelectionModel:
        sel = UserPhrasalVerbSelectionDataModel(
            id=uuid.uuid4(),
            user_id=user_id,
            phrasal_verb_id=phrasal_verb_id,
        )
        self.db.add(sel)
        await self.db.flush()
        await self.db.refresh(sel)
        return UserPhrasalVerbSelectionModel(
            id=sel.id,
            user_id=sel.user_id,
            phrasal_verb_id=sel.phrasal_verb_id,
            added_at=sel.added_at,
        )

    @log_database_operation_decorator(operation_type='delete', entity_type='user_phrasal_verb_selection')
    @trace_database_operation(operation_type='delete', table='user_phrasal_verb_selections')
    @track_database_operation(operation_type='delete', table='user_phrasal_verb_selections')
    async def remove_phrasal_verb_selection(self, user_id: UUID, phrasal_verb_id: UUID) -> bool:
        result = await self.db.execute(
            delete(UserPhrasalVerbSelectionDataModel).where(
                UserPhrasalVerbSelectionDataModel.user_id == user_id,
                UserPhrasalVerbSelectionDataModel.phrasal_verb_id == phrasal_verb_id,
            )
        )
        return result.rowcount > 0

    @staticmethod
    def _to_domain(row: UserProfileDataModel) -> UserProfileModel:
        learning_ids = [ll.language_id for ll in row.learning_languages]
        return UserProfileModel(
            id=row.id,
            user_id=row.user_id,
            native_language_id=row.native_language_id,
            learning_language_ids=learning_ids,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
