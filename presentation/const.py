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
    CONFIG = "config"


# カテゴリ定義
CAT_TRNSPORTS = "交通費精算"
CAT_BUSINESS_TRIP = "出張精算"

CATEGORIES = [
    CAT_TRNSPORTS,
    "出張申請",
    CAT_BUSINESS_TRIP,
    "海外出張申請",
    "海外出張精算",
    "経費申請",
    "経費精算",
    "交際費申請",
    "交際費精算",
]

# UI定数
BUTTONS_BASE = ["キャンセル", "確定"]
TAX_OPTIONS = [0, 8, 10]
PAYMENT_OPTIONS = ["立替", "社内精算", "カード"]

# 交通機関リスト
TRANSPORTATION = [
    "在来線（地下鉄含む）",
    "新幹線・特急（ICカード連携）",
    "新幹線・特急（WEB領収書又はEXご利用票）",
    "新幹線・特急（紙領収証）",
    "新幹線・特急（無効印チケット）",
    "タクシー",
    "タクシー（WEB領収書）",
    "私有車ガソリン代",
    "レンタカーガソリン代",
    "レンタカー料金",
    "カーシェアリング",
    "高速道路料金（紙領収書）",
    "高速道路りょうきん（ETC利用証明書）",
    "駐車料",
    "バス（高速バス除く）",
    "高速バス",
    "高速バス（ICカード決済）",
    "高速バス（乗車証明書）",
    "高速バス（WEB領収書）",
    "船舶",
    "日当",
    "上記以外（規程に準じてやむを得ない場合のみ）",
]

# サジェスト対象フィールド
SUGGESTS_TRNSPRTS = [
    "destination",
    "departure",
    "arrival",
    "car_name",
    "car_number",
    "purpose",
]

ORDER_TRNSPRTS = ["transportation"]

SUGGESTS_BUSINESS_TRIP = [
    "destination",
    "departure",
    "arrival",
    "car_name",
    "car_number",
    "purpose",
]

ORDER_BUSINESS_TRIP = ["transportation"]
