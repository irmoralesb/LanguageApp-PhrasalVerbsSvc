from uuid import UUID


class UserProfileNotFoundError(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Profile for user '{user_id}' not found.")


class UserProfileAlreadyExistsError(Exception):
    def __init__(self, user_id: UUID):
        self.user_id = user_id
        super().__init__(f"Profile for user '{user_id}' already exists.")


class LanguageNotFoundError(Exception):
    def __init__(self, language_id: UUID):
        self.language_id = language_id
        super().__init__(f"Language with id '{language_id}' not found.")
