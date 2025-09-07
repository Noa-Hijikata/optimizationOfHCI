import streamlit as st
import pandas as pd
import time, json, os
from datetime import date

st.set_page_config(page_title="経費精算 実験", layout="wide")

LOG_FILE = "logs.csv"
CONFIG_DIR = "personalized"
os.makedirs(CONFIG_DIR, exist_ok=True)

CATEGORIES = ["交通費", "宿泊費", "会議費", "物品", "その他"]
BUTTONS_BASE = ["登録", "下書き保存", "クリア"]
TAX_OPTIONS = [0, 8, 10]
PAYMENT_OPTIONS = ["立替", "社内精算", "カード"]

st.sidebar.header("実験設定")
mode = st.sidebar.radio("UIモード", ["固定UI", "パーソナライズUI"])
user_id = st.sidebar.text_input("被験者ID（必須）")
period = st.sidebar.selectbox("期間", ["2025-08", "2025-07", "2025-06"])
project = st.sidebar.text_input("プロジェクト初期値", "A-42")

if "start_time" not in st.session_state:
    st.session_state["start_time"] = None
if "rows" not in st.session_state:
    st.session_state["rows"] = []  # 明細行
if "log" not in st.session_state:
    st.session_state["log"] = []


def log_event(field, value, event="input", entity_id=None):
    st.session_state["log"].append(
        {
            "timestamp": time.time(),
            "user_id": user_id or "",
            "mode": mode,
            "event": event,
            "field": field,
            "value": value,
            "entity_id": entity_id or "",
        }
    )


def load_config(uid):
    path = os.path.join(CONFIG_DIR, f"{uid}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


# 個別設定の反映
cfg = load_config(user_id) if (mode == "パーソナライズUI" and user_id) else None
category_order = (
    cfg["category_order"] if cfg and "category_order" in cfg else CATEGORIES
)
button_order = cfg["button_order"] if cfg and "button_order" in cfg else BUTTONS_BASE
defaults = cfg.get("defaults", {}) if cfg else {}
suggest = cfg.get("suggest", {}) if cfg else {}

st.title("経費精算（実験用）")
colA, colB = st.columns([3, 2])
with colA:
    st.subheader("新規申請")
    if st.button("タスク開始", disabled=not user_id):
        st.session_state["start_time"] = time.time()
        st.session_state["rows"] = []
        st.session_state["log"] = []
        st.success("開始しました")
        log_event("task", "start", "meta")

    # クイック追加（カテゴリピル）
    st.caption("よく使う区分から追加")
    pill_cols = st.columns(len(category_order))
    for i, cat in enumerate(category_order):
        if pill_cols[i].button(
            cat + " 追加",
            use_container_width=True,
            disabled=st.session_state["start_time"] is None,
        ):
            row = {
                "id": f"r{len(st.session_state['rows'])+1}",
                "区分": cat,
                "日付": date.today(),
                "金額": 0,
                "税": defaults.get("tax", 10),
                "支払": defaults.get("payment", "立替"),
                "摘要": "",
            }
            st.session_state["rows"].append(row)
            log_event("add_row", cat, "button", entity_id=row["id"])

    # 明細編集
    for row in st.session_state["rows"]:
        with st.expander(f"明細: {row['区分']} / {row['id']}", expanded=True):
            c1, c2, c3, c4 = st.columns(4)
            new_date = c1.date_input("日付", value=row["日付"], key=row["id"] + "_d")
            if new_date != row["日付"]:
                row["日付"] = new_date
                log_event("日付", str(new_date), entity_id=row["id"])
            new_amt = c2.number_input(
                "金額", value=row["金額"], min_value=0, step=100, key=row["id"] + "_a"
            )
            if new_amt != row["金額"]:
                row["金額"] = new_amt
                log_event("金額", new_amt, entity_id=row["id"])
            new_tax = c3.selectbox(
                "税(%)",
                TAX_OPTIONS,
                index=TAX_OPTIONS.index(row["税"]) if row["税"] in TAX_OPTIONS else 2,
                key=row["id"] + "_t",
            )
            if new_tax != row["税"]:
                row["税"] = new_tax
                log_event("税", new_tax, entity_id=row["id"])
            new_pay = c4.selectbox(
                "支払方法",
                PAYMENT_OPTIONS,
                index=(
                    PAYMENT_OPTIONS.index(row["支払"])
                    if row["支払"] in PAYMENT_OPTIONS
                    else 0
                ),
                key=row["id"] + "_p",
            )
            if new_pay != row["支払"]:
                row["支払"] = new_pay
                log_event("支払", new_pay, entity_id=row["id"])

            # 区分別フィールド（交通費）
            if row["区分"] == "交通費":
                c5, c6, c7 = st.columns(3)
                stations = suggest.get(
                    "stations", ["東京", "品川", "新大阪", "大阪", "渋谷"]
                )
                from_station = c5.selectbox("出発", stations, key=row["id"] + "_fs")
                to_station = c6.selectbox("到着", stations, key=row["id"] + "_ts")
                roundtrip = c7.checkbox("往復", key=row["id"] + "_rt")
                log_event("交通費_出発", from_station, entity_id=row["id"])
                log_event("交通費_到着", to_station, entity_id=row["id"])
                log_event("交通費_往復", roundtrip, entity_id=row["id"])

            # 摘要（定型句サジェスト）
            phrases = suggest.get(
                "purpose_phrases", ["顧客訪問", "定例会議", "社内研修", "出張"]
            )
            colx, coly = st.columns([3, 1])
            new_note = colx.text_input(
                "摘要", value=row["摘要"], key=row["id"] + "_note"
            )
            if new_note != row["摘要"]:
                row["摘要"] = new_note
                log_event("摘要", new_note, entity_id=row["id"])
            if coly.selectbox("定型句", [""] + phrases, key=row["id"] + "_ph"):
                sel = coly.session_state[row["id"] + "_ph"]
                if sel:
                    row["摘要"] = (row["摘要"] + " " + sel).strip()
                    log_event("定型句", sel, "select", entity_id=row["id"])

            # 領収書
            up = st.file_uploader(
                "領収書(PDF/JPG)",
                type=["pdf", "jpg", "jpeg", "png"],
                key=row["id"] + "_up",
            )
            if up:
                log_event("upload", "receipt", "upload", entity_id=row["id"])

    # アクションボタン（順序を個別化）
    st.write("---")
    bcols = st.columns(len(button_order))
    pressed = None
    for i, lb in enumerate(button_order):
        if bcols[i].button(
            lb,
            use_container_width=True,
            disabled=st.session_state["start_time"] is None,
        ):
            pressed = lb
            break
    if pressed:
        log_event("button", pressed, "button")
        elapsed = time.time() - (st.session_state["start_time"] or time.time())
        # 保存
        df = pd.DataFrame(st.session_state["log"])
        df["elapsed_time"] = elapsed
        if not os.path.exists(LOG_FILE):
            df.to_csv(LOG_FILE, index=False)
        else:
            df.to_csv(LOG_FILE, mode="a", header=False, index=False)
        st.success(
            f"{pressed} 完了。所要時間: {elapsed:.2f}s / 明細 {len(st.session_state['rows'])}件"
        )
        st.session_state["start_time"] = None

with colB:
    st.subheader("申請サマリ")
    total = sum([r["金額"] for r in st.session_state["rows"]])
    st.metric("合計金額", f"¥{total:,}")
    st.write("現在のカテゴリ順：", " > ".join(category_order))
    st.write("現在のボタン順：", " > ".join(button_order))
    if cfg:
        st.info("個別化設定を適用中")
    elif mode == "パーソナライズUI":
        st.warning(
            "個別設定がありません。固定UIでログ収集→aggregate.pyを実行してください。"
        )
