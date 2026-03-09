class ExerciseGenerationError(Exception):
    def __init__(self, detail: str = "Failed to generate exercise."):
        self.detail = detail
        super().__init__(detail)


class LLMProviderError(Exception):
    def __init__(self, provider: str, detail: str = "LLM provider error."):
        self.provider = provider
        self.detail = detail
        super().__init__(f"[{provider}] {detail}")
