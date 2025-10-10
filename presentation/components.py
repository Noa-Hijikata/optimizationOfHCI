import streamlit as st
import time
from datetime import date
from domain.constants import TAX_OPTIONS, PAYMENT_OPTIONS


def render_expense_rows(category_order, defaults, suggest, log_usecase):
    """明細入力UI"""
    if "rows" not in st.session_state:
        st.session_state["rows"] = []

    # --- クイック追加 ---
    st.caption("よく使う区分から追加")
    pill_cols = st.columns(len(category_order))
    for i, cat in enumerate(category_order):
        if pill_cols[i].button(f"{cat} 追加", use_container_width=True):
            row = {
                "id": f"r{len(st.session_state['rows']) + 1}",
                "区分": cat,
                "日付": date.today(),
                "金額": 0,
                "税": defaults.get("tax", 10),
                "支払": defaults.get("payment", "立替"),
                "摘要": "",
            }
            st.session_state["rows"].append(row)
            log_usecase.log_event("add_row", cat, "button", row["id"])

    # --- 明細行の描画 ---
    for row in st.session_state["rows"]:
        with st.expander(f"明細: {row['区分']} / {row['id']}", expanded=True):
            render_row_editor(row, suggest, log_usecase)

    return st.session_state["rows"]


def render_row_editor(row, suggest, log_usecase):
    """明細1行の入力フォーム"""
    c1, c2, c3, c4 = st.columns(4)
    new_date = c1.date_input("日付", value=row["日付"], key=row["id"] + "_d")
    new_amt = c2.number_input(
        "金額", value=row["金額"], min_value=0, step=100, key=row["id"] + "_a"
    )
    new_tax = c3.selectbox(
        "税(%)", TAX_OPTIONS, index=TAX_OPTIONS.index(row["税"]), key=row["id"] + "_t"
    )
    new_pay = c4.selectbox(
        "支払方法",
        PAYMENT_OPTIONS,
        index=PAYMENT_OPTIONS.index(row["支払"]),
        key=row["id"] + "_p",
    )

    # 入力変更の検知とログ
    for field, old, new in [
        ("日付", row["日付"], new_date),
        ("金額", row["金額"], new_amt),
        ("税", row["税"], new_tax),
        ("支払", row["支払"], new_pay),
    ]:
        if old != new:
            row[field] = new
            log_usecase.log_event(field, new, entity_id=row["id"])

    # 交通費など特定区分の入力
    if row["区分"] == "交通費":
        stations = suggest.get("stations", ["東京", "品川", "新大阪", "大阪", "渋谷"])
        c5, c6, c7 = st.columns(3)
        from_s = c5.selectbox("出発", stations, key=row["id"] + "_fs")
        to_s = c6.selectbox("到着", stations, key=row["id"] + "_ts")
        rt = c7.checkbox("往復", key=row["id"] + "_rt")
        for k, v in {
            "交通費_出発": from_s,
            "交通費_到着": to_s,
            "交通費_往復": rt,
        }.items():
            log_usecase.log_event(k, v, entity_id=row["id"])

    # 摘要
    phrases = suggest.get(
        "purpose_phrases", ["顧客訪問", "定例会議", "社内研修", "出張"]
    )
    colx, coly = st.columns([3, 1])
    note = colx.text_input("摘要", value=row["摘要"], key=row["id"] + "_note")
    sel = coly.selectbox("定型句", [""] + phrases, key=row["id"] + "_ph")
    if note != row["摘要"]:
        row["摘要"] = note
        log_usecase.log_event("摘要", note, entity_id=row["id"])
    if sel:
        row["摘要"] = (row["摘要"] + " " + sel).strip()
        log_usecase.log_event("定型句", sel, "select", entity_id=row["id"])

    # 領収書
    up = st.file_uploader(
        "領収書(PDF/JPG)", type=["pdf", "jpg", "jpeg", "png"], key=row["id"] + "_up"
    )
    if up:
        log_usecase.log_event("upload", "receipt", "upload", entity_id=row["id"])


def render_summary(rows, category_order, button_order, config, mode):
    """右側のサマリパネル"""
    st.subheader("申請サマリ")
    total = sum([r["金額"] for r in rows])
    st.metric("合計金額", f"¥{total:,}")
    st.write("現在のカテゴリ順：", " > ".join(category_order))
    st.write("現在のボタン順：", " > ".join(button_order))
    if config:
        st.info("個別化設定を適用中")
    elif mode == "パーソナライズUI":
        st.warning(
            "個別設定がありません。固定UIでログ収集→aggregate.pyを実行してください。"
        )
