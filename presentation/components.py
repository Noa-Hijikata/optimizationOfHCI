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


def update_value(key, value):
    """セッション状態の値を更新するユーティリティ関数"""
    st.session_state[key] = value


def render_suggest_input(
    label, options, key_prefix, initial_value="", enable_suggest=True
):
    """
    軽量なサジェスト付き入力フィールド。
    入力フィールドと、マッチする候補のボタンを表示する。
    候補ボタンをクリックすると入力フィールドに値が自動反映される。

    Args:
        label: フィールドラベル
        options: 候補オプションのリスト
        key_prefix: Streamlit のウィジェットキー
        initial_value: 初期値
        enable_suggest: サジェスト機能を有効にするかどうか（固定UIの場合はFalse）
    """
    options = options or []

    # テキスト入力フィールド
    val = st.text_input(label, value=initial_value, key=key_prefix)

    # サジェスト機能が有効の場合のみ候補を表示
    if not enable_suggest:
        return val

    # 候補をフィルタリング（入力中の文字列にマッチするもの）
    if options and val:
        q = val.strip().lower()
        matches = [o for o in options if q in str(o).lower()][:10]

        if matches:
            st.caption("候補:")
            cols = st.columns(len(matches)) if len(matches) <= 5 else st.columns(5)
            for i, m in enumerate(matches):
                btn_key = f"{key_prefix}_s_{i}"
                if i < len(cols):
                    cols[i].button(
                        str(m),
                        key=btn_key,
                        use_container_width=True,
                        on_click=update_value,
                        args=(key_prefix, str(m)),
                    )
    elif options and not val:
        st.caption("候補:")
        cols = st.columns(len(options)) if len(options) <= 5 else st.columns(5)
        for i, m in enumerate(options):
            btn_key = f"{key_prefix}_s_{i}"
            if i < len(cols):
                cols[i].button(
                    str(m),
                    key=btn_key,
                    use_container_width=True,
                    on_click=update_value,
                    args=(key_prefix, str(m)),
                )

    return val


@st.dialog("test", width="large")
def test_dialog():
    st.write("This is a test dialog.")


@st.dialog("交通費申請", width="large")
def render_expense_form_trnsprts(task_usecase: ExpenseReport, approval_gateway=None):
    """交通費申請フォームUI"""
    st.subheader("交通費明細入力")

    config, suggests, order = {}, {}, {}
    # パーソナライズUIの場合のみサジェスト情報を取得
    enable_suggest = st.session_state.get(smi.MODE) == UIMode.PERSONALIZE.value

    if enable_suggest and st.session_state.get(smi.CONFIG):
        tr_cfg = st.session_state[smi.CONFIG].get("trnsprts_config", {})
        suggests = tr_cfg.get("suggests", {}) if isinstance(tr_cfg, dict) else {}
        order = tr_cfg.get("order", {}) if isinstance(tr_cfg, dict) else {}

    # 読み込まれた申請データがあればそれを初期値として使用
    loaded_data = st.session_state.get("loaded_submission", {})

    col11, col12, col13 = st.columns(3)
    with col11:
        user = st.text_input(
            "申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        from datetime import datetime

        date_value = date.today()
        if loaded_data.get("date"):
            try:
                date_value = datetime.strptime(loaded_data["date"], "%Y-%m-%d").date()
            except:
                pass
        exdate = st.date_input("日付", value=date_value, key="date")
    with col13:
        destination = render_suggest_input(
            "目的地",
            suggests.get("destination", []),
            "destination",
            initial_value=loaded_data.get("destination", ""),
            enable_suggest=enable_suggest,
        )

    col21, col22, col23, col24, col25 = st.columns(5)
    with col21:
        departure = render_suggest_input(
            "出発",
            suggests.get("departure", []),
            "departure",
            initial_value=loaded_data.get("departure", ""),
            enable_suggest=enable_suggest,
        )
    with col22:
        arrival = render_suggest_input(
            "到着",
            suggests.get("arrival", []),
            "arrival",
            initial_value=loaded_data.get("arrival", ""),
            enable_suggest=enable_suggest,
        )
    with col23:
        is_roundtrip = st.checkbox(
            "往復", value=loaded_data.get("is_roundtrip", False), key="is_roundtrip"
        )
    with col24:
        amount = st.number_input(
            "金額",
            min_value=0,
            step=100,
            value=loaded_data.get("amount", 0),
            key="amount",
        )
    with col25:
        # 預を考慈した合計金額を計算して表示
        calculated_total = amount * (2 if is_roundtrip else 1)
        st.metric("合計金額", f"¥{calculated_total:,}")

    col31, col32, col33, col34 = st.columns(4)
    with col31:
        car_name = render_suggest_input(
            "車名",
            suggests.get("car_name", []),
            "car_name",
            initial_value=loaded_data.get("car_name", ""),
            enable_suggest=enable_suggest,
        )
    with col32:
        car_number = render_suggest_input(
            "ナンバー",
            suggests.get("car_number", []),
            "car_number",
            initial_value=loaded_data.get("car_number", ""),
            enable_suggest=enable_suggest,
        )
    with col33:
        transportation = st.selectbox(
            "交通機関",
            order.get("transportation", TRANSPORTATION),
            index=(
                order.get("transportation", TRANSPORTATION).index(
                    loaded_data.get("transportation")
                )
                if loaded_data.get("transportation")
                in order.get("transportation", TRANSPORTATION)
                else 0
            ),
            key="transportation",
        )
    with col34:
        uploaded_file = st.file_uploader(
            "領収書(PDF/JPG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="uploaded_file",
        )

    purpose = render_suggest_input(
        "交通目的",
        suggests.get("purpose", []),
        "purpose",
        initial_value=loaded_data.get("purpose", ""),
        enable_suggest=enable_suggest,
    )

    # submitted = st.form_submit_button("確定")
    bcols = st.columns(len(BUTTONS_BASE))
    pressed = None
    # 合計金額を計算
    calculated_total = amount * (2 if is_roundtrip else 1)
    form_data = {
        "user": user,
        "date": str(exdate),
        "destination": destination,
        "departure": departure,
        "arrival": arrival,
        "is_roundtrip": is_roundtrip,
        "amount": amount,
        "total": calculated_total,
        "car_name": car_name,
        "car_number": car_number,
        "transportation": transportation,
        "purpose": purpose,
        "uploaded_file": bool(uploaded_file),
    }
    for i, lb in enumerate(BUTTONS_BASE):
        if bcols[i].button(
            lb,
            use_container_width=True,
        ):
            if lb == "確定":
                action = ActionType.SUBMIT.value
                task_usecase.add_event(
                    event=EventType.FORMSUBMIT.value,
                    action=ActionType.SUBMIT.value,
                    value=form_data,
                )
                # DB に申請を保存
                if approval_gateway:
                    approval_gateway.add_submission(
                        user_id=user,
                        category="交通費精算",
                        data=form_data,
                    )
            else:
                action = ActionType.CANCEL.value

            pressed = lb

    if pressed:
        # task_usecase.add_event(
        #     event=EventType.FORMSUBMIT.value,
        #     category="交通費申請",
        #     action=pressed,
        # )
        if lb == "確定":
            st.session_state["submission_success"] = "交通費明細を申請しました"
        st.success(f"交通費明細を{pressed}しました。")
        st.session_state[smi.CATEGORY] = None

        # キャンセル時はセッション状態をクリアして次回は空白状態にする
        if lb == "キャンセル":
            # フォーム関連のキーをすべてクリア
            form_keys = [
                "date",
                "destination",
                "destination_selected",
                "departure",
                "departure_selected",
                "arrival",
                "arrival_selected",
                "is_roundtrip",
                "amount",
                "total",
                "car_name",
                "car_name_selected",
                "car_number",
                "car_number_selected",
                "transportation",
                "purpose",
                "purpose_selected",
                "uploaded_file",
                "loaded_submission",
            ]
            for key in form_keys:
                if key in st.session_state:
                    del st.session_state[key]

        st.rerun()


@st.dialog("出張費申請", width="large")
def render_expense_form_businessTrip(
    task_usecase: ExpenseReport, approval_gateway=None
):
    """出張申請フォームUI"""
    st.subheader("出張費明細入力")

    config, suggests, order = {}, {}, {}
    # パーソナライズUIの場合のみサジェスト情報を取得
    enable_suggest = st.session_state.get(smi.MODE) == UIMode.PERSONALIZE.value

    if enable_suggest and st.session_state.get(smi.CONFIG):
        bt_cfg = st.session_state[smi.CONFIG].get("bussinessTrip_config", {})
        suggests = bt_cfg.get("suggests", {}) if isinstance(bt_cfg, dict) else {}
        order = bt_cfg.get("order", {}) if isinstance(bt_cfg, dict) else {}

    # 読み込まれた申請データがあればそれを初期値として使用
    loaded_data = st.session_state.get("loaded_submission", {})

    col11, col12, col13, col14 = st.columns(4)
    with col11:
        user = st.text_input(
            "申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        from datetime import datetime

        date_from_value = date.today()
        if loaded_data.get("date_from"):
            try:
                date_from_value = datetime.strptime(
                    loaded_data["date_from"], "%Y-%m-%d"
                ).date()
            except:
                pass
        date_from = st.date_input(
            "出張日（from）",
            value=date_from_value,
            key="date_from",
        )

    with col13:
        date_to_value = date.today()
        if loaded_data.get("date_to"):
            try:
                date_to_value = datetime.strptime(
                    loaded_data["date_to"], "%Y-%m-%d"
                ).date()
            except:
                pass
        date_to = st.date_input(
            "出張日（To）",
            value=date_to_value,
            key="date_to",
        )
    with col14:
        destination = render_suggest_input(
            "出張先",
            suggests.get("destination", []),
            "destination_trip",
            initial_value=loaded_data.get("destination", ""),
            enable_suggest=enable_suggest,
        )

    col21, col22, col23, col24, col25 = st.columns(5)
    with col21:
        departure = render_suggest_input(
            "出発",
            suggests.get("departure", []),
            "departure_trip",
            initial_value=loaded_data.get("departure", ""),
            enable_suggest=enable_suggest,
        )
    with col22:
        arrival = render_suggest_input(
            "到着",
            suggests.get("arrival", []),
            "arrival_trip",
            initial_value=loaded_data.get("arrival", ""),
            enable_suggest=enable_suggest,
        )
    with col23:
        is_roundtrip = st.checkbox(
            "往復",
            value=loaded_data.get("is_roundtrip", False),
            key="is_roundtrip_trip",
        )
    with col24:
        amount = st.number_input(
            "金額",
            min_value=0,
            step=100,
            value=loaded_data.get("amount", 0),
            key="amount_trip",
        )
    with col25:
        # 預を考慈した合計金額を計算して表示
        calculated_total = amount * (2 if is_roundtrip else 1)
        st.metric("合計金額", f"¥{calculated_total:,}")

    col31, col32, col33, col34 = st.columns(4)
    with col31:
        car_name = render_suggest_input(
            "車名",
            suggests.get("car_name", []),
            "car_name_trip",
            initial_value=loaded_data.get("car_name", ""),
            enable_suggest=enable_suggest,
        )
    with col32:
        car_number = render_suggest_input(
            "ナンバー",
            suggests.get("car_number", []),
            "car_number_trip",
            initial_value=loaded_data.get("car_number", ""),
            enable_suggest=enable_suggest,
        )
    with col33:
        transportation_idx = 0
        if loaded_data.get("transportation") and loaded_data.get(
            "transportation"
        ) in order.get("transportation", TRANSPORTATION):
            transportation_idx = order.get("transportation", TRANSPORTATION).index(
                loaded_data.get("transportation")
            )
        transportation = st.selectbox(
            "交通機関",
            order.get("transportation", TRANSPORTATION),
            index=transportation_idx,
            key="transportation_trip",
        )
    with col34:
        uploaded_file = st.file_uploader(
            "領収書(PDF/JPG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="uploaded_file_trip",
        )

    col41, col42, col43, col44 = st.columns(4)
    with col41:
        allowance_day = st.number_input(
            "日当日数",
            min_value=0,
            step=1,
            value=loaded_data.get("allowance_day", 0),
            key="allowance_day",
        )
    with col42:
        daily_allowance = st.number_input(
            "日当金額",
            min_value=0,
            value=loaded_data.get("daily_allowance", 0),
            key="daily_allowance",
        )
    with col43:
        accommodation_day = st.number_input(
            "宿泊日数",
            min_value=0,
            step=1,
            value=loaded_data.get("accommodation_day", 0),
            key="accommodation_day",
        )
    with col44:
        accommodation_fee = st.number_input(
            "宿泊費用",
            min_value=0,
            value=loaded_data.get("accommodation_fee", 0),
            key="accommodation_fee",
        )

    purpose = render_suggest_input(
        "出張目的",
        suggests.get("purpose", []),
        "purpose_trip",
        initial_value=loaded_data.get("purpose", ""),
        enable_suggest=enable_suggest,
    )

    # submitted = st.form_submit_button("確定")
    bcols = st.columns(len(BUTTONS_BASE))
    pressed = None
    # 合計金額を計算
    calculated_total = amount * (2 if is_roundtrip else 1)
    form_data = {
        "user": user,
        "date_from": str(date_from),
        "date_to": str(date_to),
        "destination": destination,
        "departure": departure,
        "arrival": arrival,
        "is_roundtrip": is_roundtrip,
        "amount": amount,
        "total": calculated_total,
        "car_name": car_name,
        "car_number": car_number,
        "transportation": transportation,
        "purpose": purpose,
        "allowance_day": allowance_day,
        "daily_allowance": daily_allowance,
        "accommodation_day": accommodation_day,
        "accommodation_fee": accommodation_fee,
        "uploaded_file": bool(uploaded_file),
    }
    for i, lb in enumerate(BUTTONS_BASE):
        if bcols[i].button(
            lb,
            use_container_width=True,
        ):
            if lb == "確定":
                action = ActionType.SUBMIT.value
                task_usecase.add_event(
                    event=EventType.FORMSUBMIT.value,
                    action=ActionType.SUBMIT.value,
                    value=form_data,
                )
                # DB に申請を保存
                if approval_gateway:
                    approval_gateway.add_submission(
                        user_id=user,
                        category="出張精算",
                        data=form_data,
                    )
            else:
                action = ActionType.CANCEL.value

            pressed = lb

    if pressed:
        # task_usecase.add_event(
        #     event=EventType.FORMSUBMIT.value,
        #     category="交通費申請",
        #     action=pressed,
        # )
        if lb == "確定":
            st.session_state["submission_success"] = "出張明細を申請しました"
        st.success(f"出張明細を{pressed}しました。")
        st.session_state[smi.CATEGORY] = None

        # キャンセル時はセッション状態をクリアして次回は空白状態にする
        if lb == "キャンセル":
            # フォーム関連のキーをすべてクリア
            form_keys = [
                "user",
                "date_from",
                "date_to",
                "destination",
                "departure",
                "arrival",
                "is_roundtrip",
                "amount",
                "total",
                "car_name",
                "car_number",
                "transportation",
                "purpose",
                "allowance_day",
                "daily_allowance",
                "accommodation_day",
                "accommodation_fee",
                "uploaded_file",
                "loaded_submission",
            ]
            for key in form_keys:
                if key in st.session_state:
                    del st.session_state[key]

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
