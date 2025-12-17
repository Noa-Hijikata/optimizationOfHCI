from dataclasses import dataclass


@dataclass
class LogEvent:
    timestamp: float
    user_id: str
    mode: str
    event: str
    category: str
    action: str
    value: str
    success: bool
