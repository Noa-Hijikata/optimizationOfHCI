import streamlit as st
from presentation.sidebar import render_sidebar
from presentation.components import render_expense_rows, render_summary
from usecases.expenseReport import ExpenseReport
from usecases.personalization import Personalization
from usecases.logging import Logging
from domain.constants import CATEGORIES, BUTTONS_BASE


def run_app():
    st.set_page_config(page_title="経費精算 実験", layout="wide")

    # --- サイドバー（設定入力） ---
    user_config = render_sidebar()

    # --- ユースケース層を初期化 ---
    log_usecase = Logging(log_path="data/logs.csv")
    config_usecase = Personalization(config_dir="personalized")
    task_usecase = ExpenseReport(log_usecase, config_usecase)

    # --- パーソナライズ設定読込 ---
    config = None
    if user_config["mode"] == "パーソナライズUI" and user_config["user_id"]:
        config = config_usecase.load_config(user_config["user_id"])

    category_order = config.get("category_order", CATEGORIES) if config else CATEGORIES
    button_order = config.get("button_order", BUTTONS_BASE) if config else BUTTONS_BASE
    defaults = config.get("defaults", {}) if config else {}
    suggest = config.get("suggest", {}) if config else {}

    # --- メインUI ---
    st.title("経費精算（実験用）")
    colA, colB = st.columns([3, 2])

    with colA:
        task_usecase.render_task_start(user_config["user_id"])
        rows = render_expense_rows(category_order, defaults, suggest, log_usecase)
        pressed = task_usecase.render_action_buttons(button_order)
        if pressed:
            task_usecase.save_logs(user_config["user_id"], user_config["mode"], rows)
    with colB:
        render_summary(rows, category_order, button_order, config, user_config["mode"])
