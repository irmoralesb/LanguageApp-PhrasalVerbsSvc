from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.exercise_model import ExerciseHistoryRecord, PhrasalVerbStats


class ExerciseRepositoryInterface(ABC):

    @abstractmethod
    async def save_result(self, record: ExerciseHistoryRecord) -> ExerciseHistoryRecord:
        ...

    @abstractmethod
    async def get_history_by_user(
        self, user_id: UUID, skip: int = 0, limit: int = 50,
    ) -> list[ExerciseHistoryRecord]:
        ...

    @abstractmethod
    async def get_stats_by_user(self, user_id: UUID) -> list[PhrasalVerbStats]:
        ...
