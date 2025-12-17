import time

from domain.Entity.logEvent import LogEvent
from infrastructure.csvRepository import CSVLogRepository


class Logging:
    def __init__(self, repo: CSVLogRepository):
        self.repo = repo

    def add_event(self, user_id, mode, event, category, action, value, success=True):
        logEvent = LogEvent(
            time.time(), user_id, mode, event, category, action, value, success
        )
        self.repo.save(logEvent)
