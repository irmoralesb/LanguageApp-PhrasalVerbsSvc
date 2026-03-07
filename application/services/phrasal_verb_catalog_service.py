from uuid import UUID

from domain.entities.phrasal_verb_model import PhrasalVerbModel
from domain.exceptions.phrasal_verb_errors import PhrasalVerbNotFoundError
from domain.interfaces.phrasal_verb_repository import PhrasalVerbRepositoryInterface


class PhrasalVerbCatalogService:

    def __init__(self, repo: PhrasalVerbRepositoryInterface):
        self.repo = repo

    async def get_catalog(self, skip: int = 0, limit: int = 100) -> list[PhrasalVerbModel]:
        return await self.repo.get_catalog(skip=skip, limit=limit)

    async def get_by_id(self, phrasal_verb_id: UUID) -> PhrasalVerbModel:
        pv = await self.repo.get_by_id(phrasal_verb_id)
        if pv is None:
            raise PhrasalVerbNotFoundError(phrasal_verb_id)
        return pv

    async def add_to_catalog(self, pv: PhrasalVerbModel) -> PhrasalVerbModel:
        pv.is_catalog = True
        pv.created_by_user_id = None
        return await self.repo.create(pv)

    async def update_catalog_verb(
        self,
        phrasal_verb_id: UUID,
        verb: str,
        particle: str,
        definition: str,
        example_sentence: str | None,
    ) -> PhrasalVerbModel:
        existing = await self.repo.get_by_id(phrasal_verb_id)
        if existing is None:
            raise PhrasalVerbNotFoundError(phrasal_verb_id)
        existing.verb = verb
        existing.particle = particle
        existing.definition = definition
        existing.example_sentence = example_sentence
        updated = await self.repo.update(existing)
        if updated is None:
            raise PhrasalVerbNotFoundError(phrasal_verb_id)
        return updated

    async def delete_catalog_verb(self, phrasal_verb_id: UUID) -> bool:
        existing = await self.repo.get_by_id(phrasal_verb_id)
        if existing is None:
            raise PhrasalVerbNotFoundError(phrasal_verb_id)
        return await self.repo.delete(phrasal_verb_id)

    async def add_custom_verb(self, user_id: UUID, pv: PhrasalVerbModel) -> PhrasalVerbModel:
        pv.is_catalog = False
        pv.created_by_user_id = user_id
        return await self.repo.create(pv)

    async def get_user_custom_verbs(self, user_id: UUID) -> list[PhrasalVerbModel]:
        return await self.repo.get_by_user(user_id)
