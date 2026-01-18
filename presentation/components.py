import streamlit as st

import datetime

from presentation.const import (
    EventType,
    UIMode,
    SessionManagementItems as smi,
    ActionType,
)
from domain.constants import TAX_OPTIONS, PAYMENT_OPTIONS, TRANSPORTATION, BUTTONS_BASE
from usecases.expenseReport import ExpenseReport
from usecases.aiAgent import AIAgent
from utils.utils import safe_strftime, parse_ai_response

import time
import dotenv
import logging


def update_value(key, value):
    """セッション状態の値を更新するユーティリティ関数"""
    st.session_state[key] = value


def render_suggest_input(
    label, options, initial_value, key_prefix, enable_suggest=True
):
    """
    軽量なサジェスト付き入力フィールド。
    入力フィールドと、マッチする候補のボタンを表示する。
    候補ボタンをクリックすると入力フィールドに値が自動反映される。

    Args:
        label: フィールドラベル
        options: 候補オプションのリスト
        key_prefix: Streamlit のウィジェットキー
        enable_suggest: サジェスト機能を有効にするかどうか（固定UIの場合はFalse）
    """
    options = options or []

    # セッションに既存値があれば壊さず、存在しなければ初期値をセット
    st.session_state.setdefault(key_prefix, initial_value)
    # ウィジェットは key のみ渡す（value を毎回渡すと警告になる）
    val = st.text_input(label, key=key_prefix)

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


def del_form_key_session_state():
    print("del_form_key_session_state called")
    """フォーム関連のキーをすべてクリア"""
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
        "date_from",
        "date_to",
        "destination_trip",
        "departure_trip",
        "arrival_trip",
        "is_roundtrip_trip",
        "amount_trip",
        "total_trip",
        "car_name_trip",
        "car_number_trip",
        "transportation_trip",
        "purpose_trip",
        "allowance_day",
        "daily_allowance",
        "accommodation_day",
        "accommodation_fee",
        "uploaded_file_trip",
        "loaded_submission",
        "form_data_to_apply",
        "apply_ai_data",
        smi.CATEGORY,
    ]
    for key in form_keys:
        if key in st.session_state:
            del st.session_state[key]


@st.dialog("💼 交通費申請", width="large", on_dismiss=del_form_key_session_state)
def render_expense_form_trnsprts(task_usecase: ExpenseReport, approval_gateway=None):
    """交通費申請フォームUI"""
    st.markdown(
        "<div style='background: linear-gradient(90deg, #2E86AB22, #A23B7222); padding: 15px; border-radius: 8px; margin-bottom: 20px;'><h3 style='color: #2E86AB; margin: 0;'>🚗 交通費明細入力</h3></div>",
        unsafe_allow_html=True,
    )

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
            "👤 申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        exdate = st.date_input("📅 日付", key="date")
    with col13:

        destination = render_suggest_input(
            label="🎯 目的地",
            options=suggests.get("destination", []),
            initial_value=loaded_data.get("destination", ""),
            key_prefix="destination",
            enable_suggest=enable_suggest,
        )

    # 区間情報セクション
    st.markdown(
        "<div style='background: #2E86AB11; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #2E86AB; font-weight: bold;'>📍 区間情報</span></div>",
        unsafe_allow_html=True,
    )
    col21, col22, col23 = st.columns(3)
    with col21:
        departure = render_suggest_input(
            label="📍 出発",
            options=suggests.get("departure", []),
            initial_value=loaded_data.get("departure", ""),
            key_prefix="departure",
            enable_suggest=enable_suggest,
        )
    with col22:
        arrival = render_suggest_input(
            label="🏁 到着",
            options=suggests.get("arrival", []),
            key_prefix="arrival",
            initial_value=loaded_data.get("arrival", ""),
            enable_suggest=enable_suggest,
        )
    with col23:

        is_roundtrip = st.checkbox("🔄 往復", key="is_roundtrip")

    # 金額情報セクション
    st.markdown(
        "<div style='background: #06A77D11; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #06A77D; font-weight: bold;'>💰 金額情報</span></div>",
        unsafe_allow_html=True,
    )
    col_amount_l, col_amount_r = st.columns(2)
    with col_amount_l:
        st.session_state.setdefault("amount", loaded_data.get("amount", 0))
        amount = st.number_input(
            "💰 金額",
            min_value=0,
            step=100,
            key="amount",
        )
    with col_amount_r:
        # 往復を考慮した合計金額を計算して表示
        calculated_total = amount * (2 if is_roundtrip else 1)
        st.metric("合計金額", f"¥{calculated_total:,}")

    # 車両情報セクション
    st.markdown(
        "<div style='background: #A23B7211; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #A23B72; font-weight: bold;'>🚙 車両情報</span></div>",
        unsafe_allow_html=True,
    )
    col31, col32, col33, col34 = st.columns(4)
    with col31:

        car_name = render_suggest_input(
            label="🚗 車名",
            options=suggests.get("car_name", []),
            initial_value=loaded_data.get("car_name", ""),
            key_prefix="car_name",
            enable_suggest=enable_suggest,
        )
    with col32:

        car_number = render_suggest_input(
            "🔢 ナンバー",
            options=suggests.get("car_number", []),
            initial_value=loaded_data.get("car_number", ""),
            key_prefix="car_number",
            enable_suggest=enable_suggest,
        )
    with col33:
        transportation = st.selectbox(
            "🚌 交通機関",
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
            "📄 領収書(PDF/JPG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="uploaded_file",
        )

    # 備考セクション
    st.markdown(
        "<div style='background: #F1800111; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #F18F01; font-weight: bold;'>📝 備考</span></div>",
        unsafe_allow_html=True,
    )

    purpose = render_suggest_input(
        label="交通目的",
        options=suggests.get("purpose", []),
        initial_value=loaded_data.get("purpose", ""),
        key_prefix="purpose",
        enable_suggest=enable_suggest,
    )

    # submitted = st.form_submit_button("確定")
    st.markdown(
        "<div style='background: linear-gradient(90deg, #2E86AB11, #A23B7211); padding: 15px; border-radius: 8px; margin: 20px 0;'></div>",
        unsafe_allow_html=True,
    )

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
            f"✅ {lb}" if lb == "確定" else f"❌ {lb}",
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
                st.session_state["submission_success"] = "交通費明細を申請しました"
            else:
                action = ActionType.CANCEL.value

            st.success(f"交通費明細を{lb}しました。")
            st.session_state[smi.CATEGORY] = None

            # フォームキーをセッション状態から削除するユーティリティ関数を呼び出す
            del_form_key_session_state()
            st.rerun()


@st.dialog("✈️ 出張費申請", width="large", on_dismiss=del_form_key_session_state)
def render_expense_form_businessTrip(
    task_usecase: ExpenseReport, approval_gateway=None
):
    """出張申請フォームUI"""
    st.markdown(
        "<div style='background: linear-gradient(90deg, #A23B7222, #F1800122); padding: 15px; border-radius: 8px; margin-bottom: 20px;'><h3 style='color: #A23B72; margin: 0;'>✈️ 出張費明細入力</h3></div>",
        unsafe_allow_html=True,
    )

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
            "👤 申請者",
            disabled=True if st.session_state.get(smi.USER_ID, False) else False,
            value=st.session_state.get(smi.USER_ID, ""),
            key="user",
        )
    with col12:
        date_from = st.date_input(
            "📅 出張日（From）",
            key="date_from",
        )

    with col13:
        date_to = st.date_input(
            "📅 出張日（To）",
            key="date_to",
        )
    with col14:

        destination = render_suggest_input(
            label="🌍 出張先",
            options=suggests.get("destination", []),
            initial_value=loaded_data.get("destination", ""),
            key_prefix="destination_trip",
            enable_suggest=enable_suggest,
        )

    # 区間情報セクション
    st.markdown(
        "<div style='background: #2E86AB11; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #2E86AB; font-weight: bold;'>📍 区間情報</span></div>",
        unsafe_allow_html=True,
    )
    col21, col22, col23 = st.columns(3)
    with col21:

        departure = render_suggest_input(
            label="📍 出発",
            options=suggests.get("departure", []),
            key_prefix="departure_trip",
            initial_value=loaded_data.get("departure", ""),
            enable_suggest=enable_suggest,
        )
    with col22:

        arrival = render_suggest_input(
            label="🏁 到着",
            options=suggests.get("arrival", []),
            key_prefix="arrival_trip",
            initial_value=loaded_data.get("arrival", ""),
            enable_suggest=enable_suggest,
        )
    with col23:

        is_roundtrip = st.checkbox(
            "🔄 往復",
            key="is_roundtrip_trip",
        )

    # 交通費セクション
    st.markdown(
        "<div style='background: #06A77D11; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #06A77D; font-weight: bold;'>💰 交通費</span></div>",
        unsafe_allow_html=True,
    )
    col_amt_l, col_amt_r = st.columns(2)
    with col_amt_l:
        st.session_state.setdefault("amount_trip", loaded_data.get("amount", 0))
        amount = st.number_input(
            "💰 金額",
            min_value=0,
            step=100,
            key="amount_trip",
        )
    with col_amt_r:
        # 往復を考慮した合計金額を計算して表示
        calculated_total = amount * (2 if is_roundtrip else 1)
        st.metric("合計交通費", f"¥{calculated_total:,}")

    # 車両情報セクション
    st.markdown(
        "<div style='background: #A23B7211; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #A23B72; font-weight: bold;'>🚙 車両情報</span></div>",
        unsafe_allow_html=True,
    )
    col31, col32, col33, col34 = st.columns(4)
    with col31:

        car_name = render_suggest_input(
            label="🚗 車名",
            options=suggests.get("car_name", []),
            key_prefix="car_name_trip",
            initial_value=loaded_data.get("car_name", ""),
            enable_suggest=enable_suggest,
        )
    with col32:

        car_number = render_suggest_input(
            label="🔢 ナンバー",
            options=suggests.get("car_number", []),
            key_prefix="car_number_trip",
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
            "🚌 交通機関",
            order.get("transportation", TRANSPORTATION),
            index=transportation_idx,
            key="transportation_trip",
        )
    with col34:
        uploaded_file = st.file_uploader(
            "📄 領収書(PDF/JPG)",
            type=["pdf", "jpg", "jpeg", "png"],
            key="uploaded_file_trip",
        )

    # 手当・宿泊費セクション
    st.markdown(
        "<div style='background: #F1800111; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #F18F01; font-weight: bold;'>🏨 手当・宿泊費</span></div>",
        unsafe_allow_html=True,
    )
    col41, col42, col43, col44 = st.columns(4)
    with col41:
        st.session_state.setdefault(
            "allowance_day", loaded_data.get("allowance_day", 0)
        )
        allowance_day = st.number_input(
            "📋 日当日数",
            min_value=0,
            step=1,
            key="allowance_day",
        )
    with col42:
        st.session_state.setdefault(
            "daily_allowance", loaded_data.get("daily_allowance", 0)
        )
        daily_allowance = st.number_input(
            "💷 日当金額",
            min_value=0,
            key="daily_allowance",
        )
    with col43:
        st.session_state.setdefault(
            "accommodation_day", loaded_data.get("accommodation_day", 0)
        )
        accommodation_day = st.number_input(
            "🏨 宿泊日数",
            min_value=0,
            step=1,
            key="accommodation_day",
        )
    with col44:
        st.session_state.setdefault(
            "accommodation_fee", loaded_data.get("accommodation_fee", 0)
        )
        accommodation_fee = st.number_input(
            "💵 宿泊費用",
            min_value=0,
            key="accommodation_fee",
        )

    # 備考セクション
    st.markdown(
        "<div style='background: #2E86AB11; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #2E86AB; font-weight: bold;'>📝 備考</span></div>",
        unsafe_allow_html=True,
    )

    purpose = render_suggest_input(
        label="出張目的",
        options=suggests.get("purpose", []),
        key_prefix="purpose_trip",
        initial_value=loaded_data.get("purpose", ""),
        enable_suggest=enable_suggest,
    )

    # submitted = st.form_submit_button("確定")
    st.markdown(
        "<div style='background: linear-gradient(90deg, #A23B7211, #F1800111); padding: 15px; border-radius: 8px; margin: 20px 0;'></div>",
        unsafe_allow_html=True,
    )

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
            f"✅ {lb}" if lb == "確定" else f"❌ {lb}",
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
                st.session_state["submission_success"] = "出張明細を申請しました"
            else:
                action = ActionType.CANCEL.value

            st.success(f"出張明細を{lb}しました。")
            st.success(f"出張明細を{lb}しました。")
            st.session_state[smi.CATEGORY] = None

            # フォームキーをセッション状態から削除するユーティリティ関数を呼び出す
            del_form_key_session_state()

            st.rerun()


def render_summary(category_order, button_order, config, mode):
    """右側のサマリパネル（固定 / スクロール追従）を表示します。

    CSSで幅と位置を調整し、デスクトップでは画面右端に固定表示、
    スクロール時は top に従って追従する（sticky）ようにします。
    """

    # Sticky + Fixed のハイブリッド CSS:
    # - モバイルや狭い画面では position: sticky を使い、カラム内で追従
    # - ある幅以上（デスクトップ想定）では fixed にして画面右端に固定
    css = """
    <style>
    /* wrapper */
    #right-summary {
      position: -webkit-sticky;
      position: sticky;
      top: 80px;
      align-self: flex-start;
      z-index: 9999;
      padding-bottom: 40px;
    }

    /* 大画面では右端に固定表示し、幅を確保 */
    @media (min-width: 1000px) {
      #right-summary {
        position: fixed !important;
        right: 24px;
        top: 80px;
        width: 300px;
      }
      /* メインコンテンツとの重なりを抑えるため、右カラムの直前に適度な余白を入れる */
      .css-1l02zno.e1fqkh3o2 { margin-right: 340px; }
    }

    /* 微調整: モバイル時の横幅オーバーを防ぐ */
    @media (max-width: 999px) {
      #right-summary { width: auto; }
    }
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    st.markdown("<div id='right-summary'>", unsafe_allow_html=True)

    if config:
        st.markdown(
            "<div style='background: linear-gradient(90deg, #06A77D22, #06A77D44); padding: 12px; border-radius: 8px; border-left: 4px solid #06A77D;'>✅ 個別化設定を適用中</div>",
            unsafe_allow_html=True,
        )
    elif mode == UIMode.PERSONALIZE.value:
        st.markdown(
            "<div style='background: linear-gradient(90deg, #F1800122, #F1800144); padding: 12px; border-radius: 8px; border-left: 4px solid #F18F01;'>ℹ️ 新規ユーザで実行中</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def render_ai_chat_panel(ai_agent: AIAgent, user_id, approval_gateway):
    """右側パネル用のAIチャット（`st.sidebar` ではなく通常のカラム内で表示）。"""

    st.markdown(
        "<div style='padding: 6px 0;'><h4>🤖 AIアシスタント</h4></div>",
        unsafe_allow_html=True,
    )

    # チャット履歴をセッション状態に保持（キーは文字列で管理）
    if "ai_chat_history" not in st.session_state:
        st.session_state["ai_chat_history"] = []

    # チャット履歴を表示
    for chat in st.session_state["ai_chat_history"]:
        if chat["role"] == "user":
            st.markdown(f"**あなた:** {chat['message']}")
        else:
            st.markdown(f"**アシスタント:** {chat['message']}")

    # ユーザー入力
    user_input = st.text_input(
        "AIに話しかける",
        key="ai_chat_input",
        placeholder="例: 昨日と同じ内容で申請したい",
        label_visibility="collapsed",
    )

    if st.button("送信", key="ai_chat_send", use_container_width=True) and user_input:
        # ユーザーメッセージを履歴に追加
        # 送信前の履歴を取得してAIに渡すことで、現在の入力に対するコンテキストとする
        history = st.session_state["ai_chat_history"].copy()
        st.session_state["ai_chat_history"].append(
            {"role": "user", "message": user_input}
        )

        with st.spinner("AIが考え中..."):
            # 1. 意図解釈
            intent_result = ai_agent.interpret_command(user_input, history=history)

            # エラーが発生した場合は履歴に表示して終了
            if isinstance(intent_result, str) and intent_result.startswith(
                "(AI error)"
            ):
                st.session_state["ai_chat_history"].append(
                    {"role": "ai", "message": intent_result}
                )
                st.rerun()

            print("AI intent_result:", intent_result)

            # 2. 検索と絞り込み or 新規提案
            result = ai_agent.apply_intent(intent_result, user_id)

            if result["status"] == "success":
                # AIがカテゴリを特定している場合は反映
                if "category" in result:
                    st.session_state[smi.CATEGORY] = result["category"]

                msg = result.get("message", "内容をフォームに反映しました。")
                st.session_state["ai_chat_history"].append(
                    {"role": "ai", "message": msg}
                )
                st.session_state["form_data_to_apply"] = result["data"]
                st.session_state["apply_ai_data"] = True
            else:
                # 絞れなかった場合、AIに聞き返させる
                clarification = ai_agent.generate_clarification(
                    user_input, history, result["status"], result.get("candidates")
                )
                st.session_state["ai_chat_history"].append(
                    {"role": "ai", "message": clarification}
                )

        try:
            # dump_session_state()
            st.rerun()
        except Exception:
            pass


def render_confirmation_with_preview(
    task_usecase: ExpenseReport,
    approval_gateway,
    user_id,
    category,
    data,
    on_success_message="申請が完了しました。",
    on_failure_message="申請に失敗しました。",
):
    """確認ダイアログとプレビュー表示"""
    st.session_state[smi.CATEGORY] = category

    # 確認メッセージ
    st.markdown(
        "<div style='background: #2ECC7111; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #2ECC71; font-weight: bold;'>✅ 確認</span></div>",
        unsafe_allow_html=True,
    )
    st.json(data, expanded=False)

    # アクションボタン
    cols = st.columns(2)
    with cols[0]:
        if st.button("確定", use_container_width=True):
            # イベントを追加
            task_usecase.add_event(
                event=EventType.FORMSUBMIT.value,
                action=ActionType.SUBMIT.value,
                value=data,
            )
            # DB に申請を保存
            approval_gateway.add_submission(
                user_id=user_id,
                category=category,
                data=data,
            )
            st.success(on_success_message)
            st.session_state["submission_success"] = on_success_message

    with cols[1]:
        if st.button("キャンセル", use_container_width=True):
            st.success("キャンセルしました。")
            st.session_state[smi.CATEGORY] = None
            st.session_state["loaded_submission"] = {}
            st.session_state["apply_ai_data"] = False

    # 過去の申請データがあれば表示
    if user_id and category:
        past_data = approval_gateway.get_past_submissions(user_id, category)
        if past_data:
            st.markdown(
                "<div style='background: #F39C1211; padding: 12px; border-radius: 8px; margin: 15px 0;'><span style='color: #F39C12; font-weight: bold;'>📂 過去の申請データ</span></div>",
                unsafe_allow_html=True,
            )
            for data in past_data:
                st.json(data, expanded=False)
                st.markdown("---")


# 確認用関数: session_state の内容をログに出力
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # 必要に応じて INFO/DEBUG に


def dump_session_state():
    try:
        snapshot = {str(k): st.session_state[k] for k in st.session_state}
        print(
            "session_state snapshot: %s",
            json.dumps(snapshot, default=str, ensure_ascii=False),
        )
    except Exception:
        logger.exception("failed to dump session_state")
