import re

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*\n?(.*?)\n?\s*```\s*$", re.DOTALL)


def strip_code_fence(text: str) -> str:
    """Remove markdown code fences (```json ... ```) that LLMs sometimes wrap around JSON."""
    m = _FENCE_RE.match(text)
    return m.group(1).strip() if m else text.strip()


EXERCISE_GENERATION_SYSTEM = (
    "You are a language teaching assistant that creates phrasal verb exercises. "
    "You MUST respond with valid JSON only, no markdown fences, no extra text."
)

EXERCISE_GENERATION_USER = """\
Create a writing exercise for the phrasal verb "{phrasal_verb}".
Definition: {definition}

The student's native language is {native_language} and they are learning {target_language}.
{situation_line}

Respond with EXACTLY this JSON structure:
{{
  "scenario_native": "<A short scenario description in {native_language} giving context>",
  "sentence_native": "<An example sentence in {native_language} that uses the concept>",
  "sentence_target": "<The same sentence translated to {target_language} using the phrasal verb '{phrasal_verb}'>"
}}
"""

EXERCISE_EVALUATION_SYSTEM = (
    "You are a language teaching assistant that evaluates student answers for phrasal verb exercises. "
    "You MUST respond with valid JSON only, no markdown fences, no extra text."
)

EXERCISE_EVALUATION_USER = """\
The student is practicing the phrasal verb "{phrasal_verb}" in {target_language}.

Expected example sentence:
{sentence_target}

Student's answer:
{user_answer}

Evaluate whether the student correctly used the phrasal verb "{phrasal_verb}" in their sentence.
The sentence does not need to be identical to the example, but the phrasal verb must be used correctly and the meaning must be appropriate.

Respond with EXACTLY this JSON structure:
{{
  "is_correct": true/false,
  "feedback": "<Explain why the answer is correct or incorrect, in the student's native language if possible>",
  "correct_example": "<If incorrect, provide the correct example sentence. If correct, set to null>"
}}
"""


def build_exercise_prompt(
    phrasal_verb: str,
    definition: str,
    native_language: str,
    target_language: str,
    situation: str | None = None,
) -> str:
    situation_line = (
        f"The student wants to practice in the context of: {situation}"
        if situation else ""
    )
    return EXERCISE_GENERATION_USER.format(
        phrasal_verb=phrasal_verb,
        definition=definition,
        native_language=native_language,
        target_language=target_language,
        situation_line=situation_line,
    )


def build_evaluation_prompt(
    phrasal_verb: str,
    target_language: str,
    sentence_target: str,
    user_answer: str,
) -> str:
    return EXERCISE_EVALUATION_USER.format(
        phrasal_verb=phrasal_verb,
        target_language=target_language,
        sentence_target=sentence_target,
        user_answer=user_answer,
    )
