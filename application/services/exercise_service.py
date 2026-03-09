import random as rand_mod
from uuid import UUID

from domain.entities.exercise_model import (
    ExercisePrompt,
    ExerciseEvaluation,
    ExerciseHistoryRecord,
    PhrasalVerbStats,
)
from domain.exceptions.exercise_errors import ExerciseGenerationError
from domain.exceptions.phrasal_verb_errors import PhrasalVerbNotFoundError
from domain.interfaces.exercise_repository import ExerciseRepositoryInterface
from domain.interfaces.phrasal_verb_repository import PhrasalVerbRepositoryInterface
from domain.interfaces.language_repository import LanguageRepositoryInterface
from domain.interfaces.llm_provider import LLMProviderInterface
from domain.interfaces.user_profile_repository import UserProfileRepositoryInterface
from domain.exceptions.user_profile_errors import UserProfileNotFoundError


class ExerciseService:

    def __init__(
        self,
        exercise_repo: ExerciseRepositoryInterface,
        phrasal_verb_repo: PhrasalVerbRepositoryInterface,
        user_profile_repo: UserProfileRepositoryInterface,
        language_repo: LanguageRepositoryInterface,
        llm_provider: LLMProviderInterface,
    ):
        self.exercise_repo = exercise_repo
        self.phrasal_verb_repo = phrasal_verb_repo
        self.user_profile_repo = user_profile_repo
        self.language_repo = language_repo
        self.llm = llm_provider

    async def generate_exercise(
        self,
        user_id: UUID,
        target_language_code: str,
        phrasal_verb_id: UUID | None = None,
        situation: str | None = None,
    ) -> ExercisePrompt:
        profile = await self.user_profile_repo.get_by_user_id(user_id)
        if profile is None:
            raise UserProfileNotFoundError(user_id)

        native_lang = await self.language_repo.get_by_id(profile.native_language_id)
        if native_lang is None:
            raise ExerciseGenerationError("Native language not found in catalog.")

        if phrasal_verb_id is not None:
            pv = await self.phrasal_verb_repo.get_by_id(phrasal_verb_id)
            if pv is None:
                raise PhrasalVerbNotFoundError(phrasal_verb_id)
        else:
            selections = await self.user_profile_repo.get_phrasal_verb_selections(user_id)
            if not selections:
                catalog = await self.phrasal_verb_repo.get_catalog(skip=0, limit=100)
                if not catalog:
                    raise ExerciseGenerationError("No phrasal verbs available.")
                pv = rand_mod.choice(catalog)
            else:
                sel = rand_mod.choice(selections)
                pv = await self.phrasal_verb_repo.get_by_id(sel.phrasal_verb_id)
                if pv is None:
                    raise PhrasalVerbNotFoundError(sel.phrasal_verb_id)

        phrasal_verb_text = f"{pv.verb} {pv.particle}"
        prompt = await self.llm.generate_exercise(
            phrasal_verb=phrasal_verb_text,
            definition=pv.definition,
            native_language=native_lang.name,
            target_language=target_language_code,
            situation=situation,
        )
        prompt.phrasal_verb_id = pv.id  # type: ignore[assignment]
        prompt.target_language_code = target_language_code
        return prompt

    async def evaluate_answer(
        self,
        user_id: UUID,
        phrasal_verb_id: UUID,
        target_language_code: str,
        scenario_native: str,
        sentence_native: str,
        sentence_target: str,
        user_answer: str,
    ) -> ExerciseEvaluation:
        pv = await self.phrasal_verb_repo.get_by_id(phrasal_verb_id)
        if pv is None:
            raise PhrasalVerbNotFoundError(phrasal_verb_id)

        phrasal_verb_text = f"{pv.verb} {pv.particle}"
        evaluation = await self.llm.evaluate_answer(
            phrasal_verb=phrasal_verb_text,
            target_language=target_language_code,
            sentence_target=sentence_target,
            user_answer=user_answer,
        )

        record = ExerciseHistoryRecord(
            id=None,
            user_id=user_id,
            phrasal_verb_id=phrasal_verb_id,
            exercise_type="writing",
            target_language_code=target_language_code,
            scenario_native=scenario_native,
            sentence_native=sentence_native,
            sentence_target=sentence_target,
            user_answer=user_answer,
            is_correct=evaluation.is_correct,
            feedback=evaluation.feedback,
        )
        await self.exercise_repo.save_result(record)

        return evaluation

    async def get_history(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExerciseHistoryRecord]:
        return await self.exercise_repo.get_history_by_user(user_id, skip=skip, limit=limit)

    async def get_stats(self, user_id: UUID) -> list[PhrasalVerbStats]:
        return await self.exercise_repo.get_stats_by_user(user_id)
