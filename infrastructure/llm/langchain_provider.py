import logging
from typing import Optional

from pydantic import BaseModel
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage

from domain.entities.exercise_model import ExercisePrompt, ExerciseEvaluation
from domain.exceptions.exercise_errors import LLMProviderError
from domain.interfaces.llm_provider import LLMProviderInterface
from infrastructure.llm.prompts import (
    EXERCISE_GENERATION_SYSTEM,
    EXERCISE_EVALUATION_SYSTEM,
    build_exercise_prompt,
    build_evaluation_prompt,
)

logger = logging.getLogger(__name__)


class _ExerciseOutput(BaseModel):
    scenario_native: str
    sentence_native: str
    sentence_target: str


class _EvaluationOutput(BaseModel):
    is_correct: bool
    feedback: str
    correct_example: Optional[str] = None


class LangChainProvider(LLMProviderInterface):
    """
    LLM provider backed by LangChain's init_chat_model.

    Supports any provider that has a langchain-<provider> integration package
    installed (e.g. openai, anthropic, google-genai, mistralai).
    To add a new provider:
      1. pip install langchain-<provider> and add it to requirements.txt.
      2. Set LLM_PROVIDER=<provider> and LLM_MODEL=<model> in the environment.
      No application code changes are required.
    """

    def __init__(
        self,
        provider: str,
        api_key: str,
        model: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> None:
        self._provider = provider
        try:
            llm = init_chat_model(
                model=model,
                model_provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
        except ImportError as exc:
            raise LLMProviderError(
                provider,
                f"Missing integration package for provider '{provider}'. "
                f"Install 'langchain-{provider}' and add it to requirements.txt. "
                f"Original error: {exc}",
            )

        self._exercise_chain = llm.with_structured_output(_ExerciseOutput)
        self._eval_chain = llm.with_structured_output(_EvaluationOutput)

    async def generate_exercise(
        self,
        phrasal_verb: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> ExercisePrompt:
        user_msg = build_exercise_prompt(
            phrasal_verb=phrasal_verb,
            definition=definition,
            native_language=native_language,
            target_language=target_language,
            situation=situation,
        )
        messages = [
            SystemMessage(content=EXERCISE_GENERATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _ExerciseOutput = await self._exercise_chain.ainvoke(messages)
            return ExercisePrompt(
                phrasal_verb_id=None,  # type: ignore[arg-type]
                phrasal_verb_text=phrasal_verb,
                target_language_code="",
                scenario_native=result.scenario_native,
                sentence_native=result.sentence_native,
                sentence_target=result.sentence_target,
            )
        except Exception as exc:
            logger.error(
                "Exercise generation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))

    async def evaluate_answer(
        self,
        phrasal_verb: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> ExerciseEvaluation:
        user_msg = build_evaluation_prompt(
            phrasal_verb=phrasal_verb,
            target_language=target_language,
            sentence_target=sentence_target,
            user_answer=user_answer,
        )
        messages = [
            SystemMessage(content=EXERCISE_EVALUATION_SYSTEM),
            HumanMessage(content=user_msg),
        ]
        try:
            result: _EvaluationOutput = await self._eval_chain.ainvoke(messages)
            return ExerciseEvaluation(
                is_correct=result.is_correct,
                feedback=result.feedback,
                correct_example=result.correct_example,
            )
        except Exception as exc:
            logger.error(
                "Answer evaluation failed (provider=%s): %s",
                self._provider,
                exc,
                exc_info=True,
            )
            raise LLMProviderError(self._provider, str(exc))
