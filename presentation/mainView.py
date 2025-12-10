import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from presentation.const import (
    UIMode,
    EventType,
    SessionManagementItems as smi,
    ActionType,
)
from domain.constants import CATEGORIES, BUTTONS_BASE, CAT_TRNSPORTS, CAT_BUSINESS_TRIP
from infrastructure.csvRepository import CSVLogRepository
from infrastructure.approvalRepository import ApprovalRepository
from presentation.sidebar import render_sidebar
from presentation.components import (
    render_summary,
    render_expense_form_trnsprts,
    render_expense_form_businessTrip,
)
from usecases.expenseReport import ExpenseReport
from usecases.personalization import Personalization
from usecases.logging import Logging


def run_app():
    st.set_page_config(page_title="経費精算 実験", layout="wide")

    # --- サイドバー（設定入力） ---
    user_config = render_sidebar()

    # --- ゲートウェイ層を初期化 ---
    log_gateway = CSVLogRepository(log_path="data/logs.csv")
    approval_gateway = ApprovalRepository(db_path="data/approvals.db")

    # --- ユースケース層を初期化 ---
    log_usecase = Logging(log_gateway)
    config_usecase = Personalization(config_dir="personalized")
    task_usecase = ExpenseReport(log_usecase)

    # --- パーソナライズ設定読込 ---
    if user_config["mode"] == UIMode.PERSONALIZE.value and user_config["user_id"]:
        st.session_state[smi.CONFIG] = config_usecase.load_config(
            user_config["user_id"]
        )

    config = st.session_state.get(smi.CONFIG)
    if config:
        category_order = config.get("category_order", CATEGORIES)
    else:
        category_order = CATEGORIES

    # --- メインUI ---
    st.title("経費精算（実験用）")
    colA, colB = st.columns([5, 2])

    with colA:
        st.subheader("新規申請")
        if st.button("タスク開始", disabled=not user_config["user_id"]):
            # --- セッション管理 ---
            if smi.USER_ID not in st.session_state:
                st.session_state[smi.USER_ID] = user_config["user_id"]
            if smi.MODE not in st.session_state:
                st.session_state[smi.MODE] = user_config["mode"]
            # --- タスク開始処理 ---
            task_usecase.start_task()

        if st.session_state.get(smi.TASK_STARTED, False):
            # --- クイック追加 ---
            st.caption("よく使う区分から追加")
            pill_cols = st.columns(len(category_order))
            for i, cat in enumerate(category_order):
                if pill_cols[i].button(cat, use_container_width=True):
                    st.session_state[smi.CATEGORY] = cat
                    task_usecase.add_event(
                        event=EventType.BUTTON.value,
                        action=ActionType.CATEGORY_SELECT,
                        value=None,
                    )
                    # print("追加")
                    # st.session_state["test_dialog"] = True

        # if st.session_state.get("test_dialog", False):
        #     test_dialog()
        if st.session_state.get(smi.CATEGORY) == CAT_TRNSPORTS:
            render_expense_form_trnsprts(task_usecase, approval_gateway)

        if st.session_state.get(smi.CATEGORY) == CAT_BUSINESS_TRIP:
            render_expense_form_businessTrip(task_usecase, approval_gateway)

        # --- 最近の申請履歴セクション（パーソナライズUIのみ） ---
        if user_config["mode"] == UIMode.PERSONALIZE.value:
            st.divider()
            st.subheader("最近の申請")
            if user_config["user_id"]:
                recent_submissions = log_gateway.get_recent_submissions(
                    user_config["user_id"], limit=3
                )
                if recent_submissions:
                    for i, submission in enumerate(recent_submissions):
                        with st.container(border=True):
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                dt_str = submission["datetime"].strftime(
                                    "%Y年%m月%d日 %H:%M"
                                )
                                category = submission["category"]
                                data = submission["data"]

                                # カテゴリに応じた情報表示
                                if category == CAT_TRNSPORTS:
                                    st.write(
                                        f"**{category}** - {data.get('destination', 'N/A')} ({dt_str})"
                                    )
                                    st.caption(
                                        f"金額: ¥{data.get('amount', 0):,} | 往復: {'はい' if data.get('is_roundtrip') else 'いいえ'}"
                                    )
                                elif category == CAT_BUSINESS_TRIP:
                                    st.write(
                                        f"**{category}** - {data.get('destination', 'N/A')} ({dt_str})"
                                    )
                                    total_cost = (
                                        data.get("amount", 0)
                                        + data.get("allowance_day", 0)
                                        * data.get("daily_allowance", 0)
                                        + data.get("accommodation_day", 0)
                                        * data.get("accommodation_fee", 0)
                                    )
                                    st.caption(
                                        f"期間: {data.get('date_from', 'N/A')} ～ {data.get('date_to', 'N/A')} | 合計: ¥{total_cost:,}"
                                    )
                                else:
                                    st.write(f"**{category}** ({dt_str})")
                            with col2:
                                if st.button("読込", key=f"load_submission_{i}"):
                                    # セッション状態に申請データを保存
                                    st.session_state[smi.USER_ID] = user_config[
                                        "user_id"
                                    ]
                                    st.session_state[smi.MODE] = user_config["mode"]
                                    st.session_state[smi.TASK_STARTED] = True
                                    st.session_state[smi.CATEGORY] = submission[
                                        "category"
                                    ]
                                    st.session_state["loaded_submission"] = submission[
                                        "data"
                                    ]
                                    st.rerun()
                else:
                    st.info("申請履歴がありません")
            else:
                st.info("ユーザーIDを入力して開始してください")

    with colB:
        render_summary(category_order, BUTTONS_BASE, config, user_config["mode"])


if __name__ == "__main__":
    run_app()
