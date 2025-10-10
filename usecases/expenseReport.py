import time


class ExpenseReport:
    def __init__(self, log_repo):
        self.log_repo = log_repo
        self.start_time = None
        self.events = []

    def start_task(self):
        self.start_time = time.time()
        self.events = []

    def log_event(self, event):
        self.events.append(event)

    def complete_task(self):
        elapsed = time.time() - (self.start_time or time.time())
        self.log_repo.save(self.events, elapsed)
        self.start_time = None
        return elapsed
