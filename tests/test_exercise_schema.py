"""Pydantic schema validation tests."""

import pytest
from pydantic import ValidationError
from uuid import uuid4

from application.schemas.exercise_schema import (
    ExerciseAnswerRequest,
    ExerciseRequest,
)


def test_exercise_request_accepts_optional_verb_and_situation() -> None:
    r = ExerciseRequest(target_language_code="en", situation="office")
    assert r.target_language_code == "en"
    assert r.situation == "office"
    assert r.phrasal_verb_id is None


def test_exercise_answer_requires_non_empty_answer() -> None:
    vid = uuid4()
    with pytest.raises(ValidationError):
        ExerciseAnswerRequest(
            phrasal_verb_id=vid,
            target_language_code="en",
            scenario_native="a",
            sentence_native="b",
            sentence_target="c",
            user_answer="",
        )


def test_exercise_answer_min_lengths() -> None:
    vid = uuid4()
    ExerciseAnswerRequest(
        phrasal_verb_id=vid,
        target_language_code="en",
        scenario_native="a",
        sentence_native="b",
        sentence_target="c",
        user_answer="x",
    )


def test_target_language_length_constraint() -> None:
    with pytest.raises(ValidationError):
        ExerciseRequest(target_language_code="e")
