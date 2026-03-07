from uuid import UUID


class ItemNotFoundError(Exception):
    """Raised when an item is not found"""

    def __init__(self, item_id: UUID):
        self.item_id = item_id
        super().__init__(f"Item with id '{item_id}' not found")


class ItemAlreadyExistsError(Exception):
    """Raised when an item with the same name already exists"""

    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Item with name '{name}' already exists")
