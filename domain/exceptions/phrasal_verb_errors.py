from uuid import UUID


class PhrasalVerbNotFoundError(Exception):
    def __init__(self, phrasal_verb_id: UUID):
        self.phrasal_verb_id = phrasal_verb_id
        super().__init__(f"Phrasal verb with id '{phrasal_verb_id}' not found.")


class PhrasalVerbAlreadyExistsError(Exception):
    def __init__(self, verb: str, particle: str):
        self.verb = verb
        self.particle = particle
        super().__init__(f"Phrasal verb '{verb} {particle}' already exists.")
