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

    # --- カスタムスタイル ---
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #2E86AB;
            --secondary-color: #A23B72;
            --accent-color: #F18F01;
            --success-color: #06A77D;
            --danger-color: #D62828;
        }
        
        /* メインコンテナのスタイル */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* ヘッダースタイル */
        h1 {
            background: linear-gradient(90deg, #2E86AB, #A23B72);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(46, 134, 171, 0.3);
        }
        
        h2, h3 {
            color: #2E86AB;
            border-left: 4px solid #F18F01;
            padding-left: 12px;
            margin-top: 20px;
        }
        
        /* ボタンスタイル */
        .stButton > button {
            background: linear-gradient(90deg, #2E86AB, #1F5A7F);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 10px 20px;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(46, 134, 171, 0.2);
        }
        
        .stButton > button:hover {
            background: linear-gradient(90deg, #1F5A7F, #2E86AB);
            box-shadow: 0 4px 12px rgba(46, 134, 171, 0.4);
            transform: translateY(-2px);
        }
        
        /* メトリクスカード */
        .stMetric {
            background: white;
            border-radius: 10px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* コンテナ */
        .stContainer {
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* 成功メッセージ */
        .stAlert-success {
            background-color: #06A77D;
            color: white;
            border-radius: 8px;
        }
        
        /* 情報メッセージ */
        .stAlert-info {
            background-color: #2E86AB;
            color: white;
            border-radius: 8px;
        }
        
        /* エラーメッセージ */
        .stAlert-error {
            background-color: #D62828;
            color: white;
            border-radius: 8px;
        }
        
        /* ラジオボタン */
        .stRadio > div {
            color: #2E86AB;
        }
        
        /* テキスト入力 */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input {
            border-radius: 6px;
            border: 2px solid #E0E0E0;
            padding: 10px 12px;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: #2E86AB;
            box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
        }
        
        /* サイドバー */
        .stSidebar {
            background: linear-gradient(180deg, #2E86AB, #1F5A7F);
            color: white;
        }
        
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: white;
            border: none;
            padding-left: 0;
        }
        
        /* キャプション */
        .stCaption {
            color: #666;
            font-weight: 500;
        }
        
        /* ディバイダー */
        hr {
            border: none;
            border-top: 2px solid #F18F01;
            margin: 20px 0;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # --- サイドバー（設定入力） ---
    user_config = render_sidebar()

    # --- UIモード変更時のセッション状態リセット ---
    if (
        smi.MODE in st.session_state
        and st.session_state[smi.MODE] != user_config["mode"]
    ):
        # モードが変わったら、フォーム関連のセッション状態をクリア
        keys_to_clear = [
            smi.CATEGORY,
            "loaded_submission",
            "show_reject_reason",
            "submission_success",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

    # --- ユーザーID変更時のセッション状態リセット ---
    if (
        smi.USER_ID in st.session_state
        and st.session_state[smi.USER_ID] != user_config["user_id"]
    ):
        # ユーザーが変わったら、タスク関連のセッション状態をクリア
        keys_to_clear = [
            smi.TASK_STARTED,
            smi.CATEGORY,
            "loaded_submission",
            "submission_success",
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

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
    else:
        # 固定UIの場合はCONFIGをクリア
        if smi.CONFIG in st.session_state:
            del st.session_state[smi.CONFIG]

    config = st.session_state.get(smi.CONFIG)
    if config:
        category_order = config.get("category_order", CATEGORIES)
    else:
        category_order = CATEGORIES

    # --- メインUI ---
    st.title("💼 経費精算システム（実験用）")

    # モード表示
    if user_config["mode"] == UIMode.PERSONALIZE.value:
        mode_badge = "🎨 パーソナライズUI"
        mode_color = "#A23B72"
    else:
        mode_badge = "📋 固定UI"
        mode_color = "#2E86AB"

    st.markdown(
        f"<div style='text-align: center; padding: 10px; background: linear-gradient(90deg, {mode_color}22, {mode_color}44); border-radius: 8px; margin-bottom: 20px;'><span style='color: {mode_color}; font-weight: bold;'>{mode_badge}</span></div>",
        unsafe_allow_html=True,
    )

    colA, colB = st.columns([5, 2])

    with colA:
        st.subheader("📝 新規申請")

        # 申請完了メッセージを表示
        if st.session_state.get("submission_success"):
            st.markdown(
                f"<div style='background: linear-gradient(90deg, #06A77D, #05885F); color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;'><span style='font-size: 18px;'>✅ {st.session_state['submission_success']}</span></div>",
                unsafe_allow_html=True,
            )
            del st.session_state["submission_success"]

        col_start, col_status = st.columns([3, 1])
        with col_start:
            if st.button(
                "🚀 タスク開始",
                disabled=not user_config["user_id"],
                use_container_width=True,
            ):
                # --- セッション管理 ---
                st.session_state[smi.USER_ID] = user_config["user_id"]
                st.session_state[smi.MODE] = user_config["mode"]
                # --- タスク開始処理 ---
                task_usecase.start_task()

        if st.session_state.get(smi.TASK_STARTED, False):
            # --- クイック追加 ---
            st.markdown(
                "<div style='background: #2E86AB11; padding: 12px; border-radius: 8px; margin-bottom: 15px;'><span style='color: #2E86AB; font-weight: bold;'>⭐ よく使う区分から追加</span></div>",
                unsafe_allow_html=True,
            )
            pill_cols = st.columns(len(category_order))
            for i, cat in enumerate(category_order):
                # カテゴリアイコンの選択
                if cat == CAT_TRNSPORTS:
                    icon = "🚗"
                elif cat == CAT_BUSINESS_TRIP:
                    icon = "✈️"
                else:
                    icon = "📋"

                with pill_cols[i]:
                    btn_label = f"{icon}\n{cat}"
                    if st.button(
                        btn_label, key=f"cat_btn_{i}", use_container_width=True
                    ):
                        st.session_state[smi.CATEGORY] = cat
                        task_usecase.add_event(
                            event=EventType.BUTTON.value,
                            action=ActionType.CATEGORY_SELECT,
                            value=None,
                        )

        if st.session_state.get(smi.CATEGORY) == CAT_TRNSPORTS:
            render_expense_form_trnsprts(task_usecase, approval_gateway)

        if st.session_state.get(smi.CATEGORY) == CAT_BUSINESS_TRIP:
            render_expense_form_businessTrip(task_usecase, approval_gateway)

        # --- 最近の申請履歴セクション（パーソナライズUIのみ） ---
        if user_config["mode"] == UIMode.PERSONALIZE.value:
            st.divider()
            st.subheader("📚 最近の申請")
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

                                # カテゴリに応じたアイコン
                                cat_icon = (
                                    "🚗"
                                    if category == CAT_TRNSPORTS
                                    else "✈️" if category == CAT_BUSINESS_TRIP else "📋"
                                )

                                # カテゴリに応じた情報表示
                                if category == CAT_TRNSPORTS:
                                    st.markdown(
                                        f"<span style='color: #2E86AB; font-weight: bold;'>{cat_icon} {category}</span> - {data.get('destination', 'N/A')}",
                                        unsafe_allow_html=True,
                                    )
                                    st.caption(
                                        f"💰 金額: ¥{data.get('amount', 0):,} | 往復: {'はい' if data.get('is_roundtrip') else 'いいえ'} | 📅 {dt_str}"
                                    )
                                elif category == CAT_BUSINESS_TRIP:
                                    st.markdown(
                                        f"<span style='color: #A23B72; font-weight: bold;'>{cat_icon} {category}</span> - {data.get('destination', 'N/A')}",
                                        unsafe_allow_html=True,
                                    )
                                    total_cost = (
                                        data.get("amount", 0)
                                        + data.get("allowance_day", 0)
                                        * data.get("daily_allowance", 0)
                                        + data.get("accommodation_day", 0)
                                        * data.get("accommodation_fee", 0)
                                    )
                                    st.caption(
                                        f"📅 期間: {data.get('date_from', 'N/A')} ～ {data.get('date_to', 'N/A')} | 💰 合計: ¥{total_cost:,}"
                                    )
                                else:
                                    st.markdown(
                                        f"<span style='color: #F18F01; font-weight: bold;'>{cat_icon} {category}</span>",
                                        unsafe_allow_html=True,
                                    )
                                    st.caption(f"📅 {dt_str}")
                            with col2:
                                if st.button(
                                    "📂 読込",
                                    key=f"load_submission_{i}",
                                    use_container_width=True,
                                ):
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
                    st.markdown(
                        "<div style='background: #06A77D22; padding: 15px; border-radius: 8px; border-left: 4px solid #06A77D;'>ℹ️ 申請履歴がありません</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div style='background: #F1800122; padding: 15px; border-radius: 8px; border-left: 4px solid #F18F01;'>ℹ️ ユーザーIDを入力して開始してください</div>",
                    unsafe_allow_html=True,
                )

    with colB:
        render_summary(category_order, BUTTONS_BASE, config, user_config["mode"])


if __name__ == "__main__":
    run_app()
