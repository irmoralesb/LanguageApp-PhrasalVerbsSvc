from fastapi import APIRouter, Depends

from application.routers.dependency_utils import (
    ExerciseSvcDep,
    CurrentUserDep,
    require_role,
)
from application.schemas.exercise_schema import (
    ExerciseRequest,
    ExercisePromptResponse,
    ExerciseAnswerRequest,
    ExerciseEvaluationResponse,
    ExerciseHistoryResponse,
    PhrasalVerbStatsResponse,
)

router = APIRouter(
    prefix="/api/v1/exercises",
    tags=["Exercises"],
    dependencies=[Depends(require_role("phrasalverbs-user"))],
)


@router.post("/generate", response_model=ExercisePromptResponse)
async def generate_exercise(
    payload: ExerciseRequest,
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    prompt = await svc.generate_exercise(
        user_id=current_user.user_id,
        target_language_code=payload.target_language_code,
        phrasal_verb_id=payload.phrasal_verb_id,
        situation=payload.situation,
    )
    return ExercisePromptResponse(
        phrasal_verb_id=prompt.phrasal_verb_id,
        phrasal_verb_text=prompt.phrasal_verb_text,
        target_language_code=prompt.target_language_code,
        scenario_native=prompt.scenario_native,
        sentence_native=prompt.sentence_native,
        sentence_target=prompt.sentence_target,
    )


@router.post("/evaluate", response_model=ExerciseEvaluationResponse)
async def evaluate_answer(
    payload: ExerciseAnswerRequest,
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    evaluation = await svc.evaluate_answer(
        user_id=current_user.user_id,
        phrasal_verb_id=payload.phrasal_verb_id,
        target_language_code=payload.target_language_code,
        scenario_native=payload.scenario_native,
        sentence_native=payload.sentence_native,
        sentence_target=payload.sentence_target,
        user_answer=payload.user_answer,
    )
    return ExerciseEvaluationResponse(
        is_correct=evaluation.is_correct,
        feedback=evaluation.feedback,
        correct_example=evaluation.correct_example,
    )


@router.get("/history", response_model=list[ExerciseHistoryResponse])
async def get_history(
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
    skip: int = 0,
    limit: int = 50,
):
    records = await svc.get_history(current_user.user_id, skip=skip, limit=limit)
    return [
        ExerciseHistoryResponse(
            id=r.id,
            phrasal_verb_id=r.phrasal_verb_id,
            exercise_type=r.exercise_type,
            target_language_code=r.target_language_code,
            scenario_native=r.scenario_native,
            sentence_native=r.sentence_native,
            sentence_target=r.sentence_target,
            user_answer=r.user_answer,
            is_correct=r.is_correct,
            feedback=r.feedback,
            created_at=r.created_at,
        )
        for r in records
    ]


@router.get("/stats", response_model=list[PhrasalVerbStatsResponse])
async def get_stats(
    svc: ExerciseSvcDep,
    current_user: CurrentUserDep,
):
    stats = await svc.get_stats(current_user.user_id)
    return [
        PhrasalVerbStatsResponse(
            phrasal_verb_id=s.phrasal_verb_id,
            verb=s.verb,
            particle=s.particle,
            correct_count=s.correct_count,
            incorrect_count=s.incorrect_count,
        )
        for s in stats
    ]
