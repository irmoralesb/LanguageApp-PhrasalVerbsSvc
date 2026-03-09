import json
import logging

from openai import AsyncOpenAI

from domain.entities.exercise_model import ExercisePrompt, ExerciseEvaluation
from domain.exceptions.exercise_errors import LLMProviderError
from domain.interfaces.llm_provider import LLMProviderInterface
from infrastructure.llm.prompts import (
    EXERCISE_GENERATION_SYSTEM,
    EXERCISE_EVALUATION_SYSTEM,
    build_exercise_prompt,
    build_evaluation_prompt,
    strip_code_fence,
)

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProviderInterface):

    def __init__(self, api_key: str, model: str, max_tokens: int = 1024, temperature: float = 0.7):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

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
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXERCISE_GENERATION_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            content = strip_code_fence(response.choices[0].message.content or "")
            data = json.loads(content)

            return ExercisePrompt(
                phrasal_verb_id=None,  # type: ignore[arg-type]
                phrasal_verb_text=phrasal_verb,
                target_language_code="",
                scenario_native=data["scenario_native"],
                sentence_native=data["sentence_native"],
                sentence_target=data["sentence_target"],
            )
        except json.JSONDecodeError as exc:
            logger.error("OpenAI returned non-JSON for exercise generation: %s", exc)
            raise LLMProviderError("openai", "Invalid JSON in exercise generation response.")
        except Exception as exc:
            logger.error("OpenAI exercise generation failed: %s", exc, exc_info=True)
            raise LLMProviderError("openai", str(exc))

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
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXERCISE_EVALUATION_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=self.max_tokens,
                temperature=0.3,
            )
            content = strip_code_fence(response.choices[0].message.content or "")
            data = json.loads(content)

            return ExerciseEvaluation(
                is_correct=bool(data["is_correct"]),
                feedback=data["feedback"],
                correct_example=data.get("correct_example"),
            )
        except json.JSONDecodeError as exc:
            logger.error("OpenAI returned non-JSON for evaluation: %s", exc)
            raise LLMProviderError("openai", "Invalid JSON in evaluation response.")
        except Exception as exc:
            logger.error("OpenAI evaluation failed: %s", exc, exc_info=True)
            raise LLMProviderError("openai", str(exc))
