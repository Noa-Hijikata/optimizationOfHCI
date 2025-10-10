from domain.Entity.logEvent import LogEvent


class Logging:
    def __init__(self, repo):
        self.repo = repo

    def add_event(self, user_id, mode, field, value, event="input", entity_id=None):
        return LogEvent.create(user_id, mode, field, value, event, entity_id)
