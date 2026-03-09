from abc import ABC, abstractmethod

from domain.entities.exercise_model import ExercisePrompt, ExerciseEvaluation


class LLMProviderInterface(ABC):

    @abstractmethod
    async def generate_exercise(
        self,
        phrasal_verb: str,
        definition: str,
        native_language: str,
        target_language: str,
        situation: str | None = None,
    ) -> ExercisePrompt:
        """Generate an exercise scenario, native sentence, and target-language example."""
        ...

    @abstractmethod
    async def evaluate_answer(
        self,
        phrasal_verb: str,
        target_language: str,
        sentence_target: str,
        user_answer: str,
    ) -> ExerciseEvaluation:
        """Evaluate the user's written answer against the expected usage."""
        ...
