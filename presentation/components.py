import streamlit as st
import time
from datetime import date

from presentation.const import (
    EventType,
    UIMode,
    SessionManagementItems as smi,
    ActionType,
)
from domain.constants import TAX_OPTIONS, PAYMENT_OPTIONS, TRANSPORTATION, BUTTONS_BASE
from usecases.expenseReport import ExpenseReport


@st.dialog("test", width="large")
def test_dialog():
    st.write("This is a test dialog.")


@st.dialog("交通費申請", width="large")
def render_expense_form_trnsprts(task_usecase: ExpenseReport):
    """交通費申請フォームUI"""
    st.subheader("交通費明細入力")

    col11, col12, col13 = st.columns(3)
    with col11:
        user = st.text_input(
            "申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        exdate = st.date_input("日付", value=date.today(), key="date")
    with col13:
        destination = st.text_input("目的地", key="destination")

    col21, col22, col23, col24, col25 = st.columns(5)
    with col21:
        departure = st.text_input("出発", key="departure")
    with col22:
        arrival = st.text_input("到着", key="arrival")
    with col23:
        is_roundtrip = st.checkbox("往復", key="is_roundtrip")
    with col24:
        amount = st.number_input("金額", min_value=0, step=100, key="amount")
    with col25:
        total = st.number_input(
            "合計金額",
            value=amount * (2 if is_roundtrip else 1),
            disabled=True,
            key="total",
        )

    col31, col32, col33, col34 = st.columns(4)
    with col31:
        car_name = st.text_input("車名", key="car_name")
    with col32:
        car_number = st.text_input("ナンバー", key="car_number")
    with col33:
        transportation = st.selectbox("交通機関", TRANSPORTATION, key="transportation")
    with col34:
        uploaded_file = st.file_uploader(
            "領収書(PDF/JPG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="uploaded_file",
        )

    purpose = st.text_input("交通目的", key="purpose")

    # submitted = st.form_submit_button("確定")
    bcols = st.columns(len(BUTTONS_BASE))
    pressed = None
    for i, lb in enumerate(BUTTONS_BASE):
        if bcols[i].button(
            lb,
            use_container_width=True,
        ):
            if lb == "確定":
                action = ActionType.SUBMIT.value
            else:
                action = ActionType.CANCEL.value

            task_usecase.add_event(
                event=EventType.FORMSUBMIT.value,
                action=ActionType.SUBMIT.value,
                value={
                    "user": user,
                    "date": str(exdate),
                    "destination": destination,
                    "departure": departure,
                    "arrival": arrival,
                    "is_roundtrip": is_roundtrip,
                    "amount": amount,
                    "total": total,
                    "car_name": car_name,
                    "car_number": car_number,
                    "transportation": transportation,
                    "purpose": purpose,
                    "uploaded_file": bool(uploaded_file),
                },
            )
            pressed = lb

    if pressed:
        # task_usecase.add_event(
        #     event=EventType.FORMSUBMIT.value,
        #     category="交通費申請",
        #     action=pressed,
        # )
        st.success(f"交通費明細を{pressed}しました。")
        st.session_state[smi.CATEGORY] = None
        st.rerun()


@st.dialog("出張費申請", width="large")
def render_expense_form_businessTrip(task_usecase: ExpenseReport):
    """出張申請フォームUI"""
    st.subheader("出張費明細入力")

    col11, col12, col13, col14 = st.columns(4)
    with col11:
        user = st.text_input(
            "申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        date_from = st.date_input(
            "出張日（from）",
            value=date.today(),
            key="date_from",
        )

    with col13:
        date_to = st.date_input(
            "出張日（To）",
            value=date.today(),
            key="date_to",
        )
    with col14:
        destination = st.text_input("出張先", key="destination")

    col21, col22, col23, col24, col25 = st.columns(5)
    with col21:
        departure = st.text_input("出発", key="departure")
    with col22:
        arrival = st.text_input("到着", key="arrival")
    with col23:
        is_roundtrip = st.checkbox("往復", key="is_roundtrip")
    with col24:
        amount = st.number_input("金額", min_value=0, step=100, key="amount")
    with col25:
        total = st.number_input(
            "合計金額",
            value=amount * (2 if is_roundtrip else 1),
            disabled=True,
            key="total",
        )

    col31, col32, col33, col34 = st.columns(4)
    with col31:
        car_name = st.text_input("車名", key="car_name")
    with col32:
        car_number = st.text_input("ナンバー", key="car_number")
    with col33:
        transportation = st.selectbox("交通機関", TRANSPORTATION, key="transportation")
    with col34:
        uploaded_file = st.file_uploader(
            "領収書(PDF/JPG)", type=["pdf", "jpg", "jpeg", "png"], key="uploaded_file"
        )

    col41, col42, col43, col44 = st.columns(4)
    with col41:
        allowance_day = st.number_input(
            "日当日数", min_value=0, step=1, key="allowance_day"
        )
    with col42:
        daily_allowance = st.number_input(
            "日当金額", min_value=0, key="daily_allowance"
        )
    with col43:
        accommodation_day = st.number_input(
            "宿泊日数", min_value=0, step=1, key="accommodation_day"
        )
    with col44:
        accommodation_fee = st.number_input(
            "宿泊費用", min_value=0, key="accommodation_fee"
        )

    purpose = st.text_input("出張目的", key="purpose")

    # submitted = st.form_submit_button("確定")
    bcols = st.columns(len(BUTTONS_BASE))
    pressed = None
    for i, lb in enumerate(BUTTONS_BASE):
        if bcols[i].button(
            lb,
            use_container_width=True,
        ):
            if lb == "確定":
                action = ActionType.SUBMIT.value
            else:
                action = ActionType.CANCEL.value

            task_usecase.add_event(
                event=EventType.FORMSUBMIT.value,
                action=ActionType.SUBMIT.value,
                value={
                    "user": user,
                    "date_from": str(date_from),
                    "date_to": str(date_to),
                    "destination": destination,
                    "departure": departure,
                    "arrival": arrival,
                    "is_roundtrip": is_roundtrip,
                    "amount": amount,
                    "total": total,
                    "car_name": car_name,
                    "car_number": car_number,
                    "transportation": transportation,
                    "purpose": purpose,
                    "allowance_day": allowance_day,
                    "daily_allowance": daily_allowance,
                    "accommodation_day": accommodation_day,
                    "accommodation_fee": accommodation_fee,
                    "uploaded_file": bool(uploaded_file),
                },
            )
            pressed = lb

    if pressed:
        # task_usecase.add_event(
        #     event=EventType.FORMSUBMIT.value,
        #     category="交通費申請",
        #     action=pressed,
        # )
        st.success(f"出張明細を{pressed}しました。")
        st.session_state[smi.CATEGORY] = None
        st.rerun()


# def render_expense_rows(category_order, defaults, suggest, task_usecase: ExpenseReport):
#     """明細入力UI"""
#     if "rows" not in st.session_state:
#         st.session_state["rows"] = []

#     # --- クイック追加 ---
#     st.caption("よく使う区分から追加")
#     pill_cols = st.columns(len(category_order))
#     for i, cat in enumerate(category_order):
#         if pill_cols[i].button(f"{cat} 追加", use_container_width=True):
#             row = {
#                 "id": f"r{len(st.session_state['rows']) + 1}",
#                 "区分": cat,
#                 "日付": date.today(),
#                 "金額": 0,
#                 "税": defaults.get("tax", 10),
#                 "支払": defaults.get("payment", "立替"),
#                 "摘要": "",
#             }
#             st.session_state["rows"].append(row)
#             task_usecase.add_event(event=EventType.BUTTON.value, category=cat)

#     # --- 明細行の描画 ---
#     for row in st.session_state["rows"]:
#         with st.expander(f"明細: {row['区分']} / {row['id']}", expanded=True):
#             render_row_editor(row, suggest, task_usecase)

#     return st.session_state["rows"]


# def render_row_editor(row, suggest, task_usecase: ExpenseReport):
#     """明細1行の入力フォーム"""
#     c1, c2, c3, c4 = st.columns(4)
#     new_date = c1.date_input("日付", value=row["日付"], key=row["id"] + "_d")
#     new_amt = c2.number_input(
#         "金額", value=row["金額"], min_value=0, step=100, key=row["id"] + "_a"
#     )
#     new_tax = c3.selectbox(
#         "税(%)", TAX_OPTIONS, index=TAX_OPTIONS.index(row["税"]), key=row["id"] + "_t"
#     )
#     new_pay = c4.selectbox(
#         "支払方法",
#         PAYMENT_OPTIONS,
#         index=PAYMENT_OPTIONS.index(row["支払"]),
#         key=row["id"] + "_p",
#     )

#     # 入力変更の検知とログ
#     for field, old, new in [
#         ("日付", row["日付"], new_date),
#         ("金額", row["金額"], new_amt),
#         ("税", row["税"], new_tax),
#         ("支払", row["支払"], new_pay),
#     ]:
#         if old != new:
#             row[field] = new
#             task_usecase.add_event(
#                 event=EventType.INPUT.value, category=field, value=new
#             )

#     # 交通費など特定区分の入力
#     if row["区分"] == "交通費":
#         stations = suggest.get("stations", ["東京", "品川", "新大阪", "大阪", "渋谷"])
#         c5, c6, c7 = st.columns(3)
#         from_s = c5.text_input("出発", stations, key=row["id"] + "_fs")
#         to_s = c6.text_input("到着", stations, key=row["id"] + "_ts")
#         rt = c7.checkbox("往復", key=row["id"] + "_rt")
#         for k, v in {
#             "交通費_出発": from_s,
#             "交通費_到着": to_s,
#             "交通費_往復": rt,
#         }.items():
#             task_usecase.add_event(event=EventType.INPUT.value, category=k, value=v)

#     # 摘要
#     phrases = suggest.get(
#         "purpose_phrases", ["顧客訪問", "定例会議", "社内研修", "出張"]
#     )
#     colx, coly = st.columns([3, 1])
#     note = colx.text_input("摘要", value=row["摘要"], key=row["id"] + "_note")
#     sel = coly.selectbox("定型句", [""] + phrases, key=row["id"] + "_ph")
#     if note != row["摘要"]:
#         row["摘要"] = note
#         task_usecase.add_event(event=EventType.INPUT.value, category="摘要", value=note)
#     if sel:
#         row["摘要"] = (row["摘要"] + " " + sel).strip()
#         task_usecase.add_event(
#             event=EventType.INPUT.value, category="定型句", value=sel
#         )

#     # 領収書
#     up = st.file_uploader(
#         "領収書(PDF/JPG)", type=["pdf", "jpg", "jpeg", "png"], key=row["id"] + "_up"
#     )
#     if up:
#         task_usecase.add_event(event=EventType.FILEUPLOAD, category="領収書(PDF/JPG)")


def render_summary(category_order, button_order, config, mode):
    """右側のサマリパネル"""
    st.subheader("申請サマリ")
    st.write("現在のカテゴリ順：", " > ".join(category_order))
    st.write("現在のボタン順：", " > ".join(button_order))
    if config:
        st.info("個別化設定を適用中")
    elif mode == UIMode.PERSONALIZE.value:
        st.info("新規ユーザで実行中")
