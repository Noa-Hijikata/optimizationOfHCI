from dataclasses import dataclass
from datetime import date
import time


@dataclass
class LogEvent:
    timestamp: float
    user_id: str
    mode: str
    event: str
    field: str
    value: str
    entity_id: str
