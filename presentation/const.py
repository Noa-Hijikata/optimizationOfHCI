from enum import Enum


class UIMode(Enum):
    PERSONALIZE = "パーソナライズUI"
    FIXED = "固定UI"


class EventType(Enum):
    INPUT = "input"
    BUTTON = "button"
    FILEUPLOAD = "upload"
    META = "meta"
    FORMSUBMIT = "form_submit"
    ERROR = "error"


class ActionType(Enum):
    ADD_ROW = "add_row"
    DELETE_ROW = "delete_row"
    SUBMIT = "submit"
    SAVE_DRAFT = "save_draft"
    CANCEL = "cancel"
    CATEGORY_SELECT = "category_select"


class SessionManagementItems(Enum):
    USER_ID = "user_id"
    MODE = "mode"
    TASK_STARTED = "task_started"
    CATEGORY = "category"
