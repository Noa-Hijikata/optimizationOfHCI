import csv
import os
from domain.Entity.logEvent import LogEvent
from gateways.logGateway import LogGateway


class CSVLogRepository(LogGateway):

    def __init__(self, log_path):
        self.log_path = log_path
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "user_id",
                        "mode",
                        "event",
                        "category",
                        "action",
                        "value",
                        "success",
                    ]
                )

    def save(self, log_event: LogEvent):
        with open(self.log_path, "a") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    log_event.timestamp,
                    log_event.user_id,
                    log_event.mode,
                    log_event.event,
                    log_event.category,
                    log_event.action,
                    log_event.value,
                    log_event.success,
                ]
            )
