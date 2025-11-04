from enum import Enum


class UIMode(Enum):
    PERSONALIZE = "パーソナライズUI"
    FIXED = "固定UI"


class EventType(Enum):
    INPUT = "input"
    BUTTON = "button"
    FILEUPLOAD = "upload"
    META = "meta"
