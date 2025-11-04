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

    # --- ユースケース層を初期化 ---
    log_usecase = Logging(log_gateway)
    config_usecase = Personalization(config_dir="personalized")
    task_usecase = ExpenseReport(log_usecase)

    # --- パーソナライズ設定読込 ---
    config = None
    if user_config["mode"] == UIMode.PERSONALIZE.value and user_config["user_id"]:
        config = config_usecase.load_config(user_config["user_id"])

    if config:
        category_order = config.get("category_order", CATEGORIES)
        button_order = config.get("button_order", BUTTONS_BASE)
        defaults = config.get("defaults", {})
        suggest = config.get("suggest", {})
    else:
        category_order = CATEGORIES
        button_order = BUTTONS_BASE
        defaults = {}
        suggest = {}

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
            render_expense_form_trnsprts(task_usecase)

        if st.session_state.get(smi.CATEGORY) == CAT_BUSINESS_TRIP:
            render_expense_form_businessTrip(task_usecase)

    with colB:
        render_summary(category_order, button_order, config, user_config["mode"])


if __name__ == "__main__":
    run_app()
