from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ExerciseRequest(BaseModel):
    phrasal_verb_id: UUID | None = Field(
        default=None,
        description="Specific phrasal verb to practice. Omit for random mode.",
    )
    target_language_code: str = Field(min_length=2, max_length=10)
    situation: str | None = Field(
        default=None,
        max_length=200,
        description="Optional context (e.g. 'office', 'street') to narrow the scenario.",
    )


class ExercisePromptResponse(BaseModel):
    phrasal_verb_id: UUID
    phrasal_verb_text: str
    target_language_code: str
    scenario_native: str
    sentence_native: str
    sentence_target: str


class ExerciseAnswerRequest(BaseModel):
    phrasal_verb_id: UUID
    target_language_code: str
    scenario_native: str
    sentence_native: str
    sentence_target: str
    user_answer: str = Field(min_length=1)


class ExerciseEvaluationResponse(BaseModel):
    is_correct: bool
    feedback: str
    correct_example: str | None = None


class ExerciseHistoryResponse(BaseModel):
    id: UUID
    phrasal_verb_id: UUID
    exercise_type: str
    target_language_code: str
    scenario_native: str
    sentence_native: str
    sentence_target: str
    user_answer: str
    is_correct: bool
    feedback: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PhrasalVerbStatsResponse(BaseModel):
    phrasal_verb_id: UUID
    verb: str
    particle: str
    correct_count: int
    incorrect_count: int
