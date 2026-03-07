from uuid import UUID

from domain.entities.user_profile_model import UserProfileModel, UserPhrasalVerbSelectionModel
from domain.exceptions.user_profile_errors import (
    UserProfileNotFoundError,
    UserProfileAlreadyExistsError,
    LanguageNotFoundError,
)
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from domain.interfaces.language_repository import LanguageRepositoryInterface


class UserProfileService:

    def __init__(
        self,
        profile_repo: UserProfileRepositoryInterface,
        language_repo: LanguageRepositoryInterface,
    ):
        self.profile_repo = profile_repo
        self.language_repo = language_repo

    async def get_profile(self, user_id: UUID) -> UserProfileModel:
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)
        return profile

    async def create_profile(
        self,
        user_id: UUID,
        native_language_id: UUID,
        learning_language_ids: list[UUID],
    ) -> UserProfileModel:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is not None:
            raise UserProfileAlreadyExistsError(user_id)

        lang = await self.language_repo.get_by_id(native_language_id)
        if lang is None:
            raise LanguageNotFoundError(native_language_id)

        for lid in learning_language_ids:
            ll = await self.language_repo.get_by_id(lid)
            if ll is None:
                raise LanguageNotFoundError(lid)

        profile = UserProfileModel(
            id=None,
            user_id=user_id,
            native_language_id=native_language_id,
            learning_language_ids=learning_language_ids,
        )
        return await self.profile_repo.create(profile)

    async def update_profile(self, user_id: UUID, native_language_id: UUID) -> UserProfileModel:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)

        lang = await self.language_repo.get_by_id(native_language_id)
        if lang is None:
            raise LanguageNotFoundError(native_language_id)

        existing.native_language_id = native_language_id
        updated = await self.profile_repo.update(existing)
        if updated is None:
            raise UserProfileNotFoundError(user_id)
        return updated

    async def add_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)
        lang = await self.language_repo.get_by_id(language_id)
        if lang is None:
            raise LanguageNotFoundError(language_id)
        await self.profile_repo.add_learning_language(user_id, language_id)

    async def remove_learning_language(self, user_id: UUID, language_id: UUID) -> None:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)
        await self.profile_repo.remove_learning_language(user_id, language_id)

    async def get_phrasal_verb_selections(self, user_id: UUID) -> list[UserPhrasalVerbSelectionModel]:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)
        return await self.profile_repo.get_phrasal_verb_selections(user_id)

    async def add_phrasal_verb_selection(
        self, user_id: UUID, phrasal_verb_id: UUID,
    ) -> UserPhrasalVerbSelectionModel:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)
        return await self.profile_repo.add_phrasal_verb_selection(user_id, phrasal_verb_id)

    async def remove_phrasal_verb_selection(self, user_id: UUID, phrasal_verb_id: UUID) -> bool:
        existing = await self.profile_repo.get_by_user_id(user_id)
        if existing is None:
            raise UserProfileNotFoundError(user_id)
        return await self.profile_repo.remove_phrasal_verb_selection(user_id, phrasal_verb_id)
