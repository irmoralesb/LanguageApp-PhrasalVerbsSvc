"""Unit tests for infrastructure.llm.prompts."""

from infrastructure.llm.prompts import (
    EXERCISE_GENERATION_SYSTEM,
    build_exercise_prompt,
    build_evaluation_prompt,
)


def test_system_prompt_is_non_empty() -> None:
    assert EXERCISE_GENERATION_SYSTEM
    assert "JSON" in EXERCISE_GENERATION_SYSTEM


def test_build_exercise_prompt_contains_inputs() -> None:
    msg = build_exercise_prompt(
        phrasal_verb="bring up",
        definition="mention",
        native_language="es",
        target_language="en",
        situation="work",
    )
    assert "bring up" in msg
    assert "mention" in msg
    assert "es" in msg and "en" in msg
    assert "work" in msg.lower() or "context" in msg.lower()


def test_build_exercise_prompt_without_situation_omits_context_line_paragraph() -> None:
    msg = build_exercise_prompt(
        phrasal_verb="run out",
        definition="finish",
        native_language="de",
        target_language="en",
        situation=None,
    )
    assert "run out" in msg
    assert "The student wants" not in msg


def test_build_evaluation_prompt_contains_sentence_and_answer() -> None:
    msg = build_evaluation_prompt(
        phrasal_verb="look up",
        target_language="en",
        sentence_target="Please look up the word.",
        user_answer="I looked up.",
    )
    assert "look up" in msg
    assert "Please look up the word." in msg
    assert "I looked up." in msg
