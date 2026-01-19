import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import dotenv  # dotenv をインポート
import logging

# .env ファイルをロード
dotenv.load_dotenv()

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
    render_ai_chat_panel,  # AIチャット右パネルをインポート
)
from usecases.expenseReport import ExpenseReport
from usecases.personalization import Personalization
from usecases.logging import Logging
from usecases.aiAgent import AIAgent  # AI Agent をインポート

import logging
from logging.handlers import RotatingFileHandler

os.makedirs("logs", exist_ok=True)
handler = RotatingFileHandler(
    "logs/app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(logging.INFO)
root.addHandler(handler)
# 既にストリームハンドラが無ければ標準出力にも出す
if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root.addHandler(stream_handler)


def run_app():
    st.set_page_config(page_title="経費精算 実験", layout="wide")

    # region --- カスタムスタイル ---
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #FF8C00;
            --secondary-color: #555555;
            --accent-color: #FFA500;
            --background-color: #FFFFFF;
            --sidebar-bg: #F8F9FA;
            --text-color: #262730;
        }
        
        /* メインコンテナのスタイル */
        .main {
            background-color: var(--background-color);
        }
        
        /* ヘッダースタイル */
        h1 {
            color: var(--primary-color);
            background: transparent;
            padding: 10px 0;
            border-bottom: 2px solid var(--primary-color);
            border-radius: 0;
            text-align: left;
            box-shadow: none;
            font-weight: 700;
        }
        
        h2, h3 {
            color: var(--text-color);
            border-left: 4px solid var(--primary-color);
            padding-left: 12px;
            margin-top: 25px;
            font-weight: 600;
        }
        
        /* ボタンスタイル */
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            padding: 8px 16px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(255, 140, 0, 0.2);
        }
        
        .stButton > button:hover {
            background: #E67E00;
            box-shadow: 0 4px 8px rgba(255, 140, 0, 0.3);
            transform: translateY(-1px);
        }
        
        /* メトリクスカード */
        .stMetric {
            background: white;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        }
        
        /* コンテナ */
        .stContainer {
            border-radius: 12px;
            background: white;
            border: 1px solid #E0E0E0;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            padding: 20px;
        }
        
        /* 成功メッセージ */
        .stAlert-success {
            background-color: #FFF4E5;
            color: #663C00;
            border: 1px solid #FFD599;
            border-radius: 8px;
        }
        
        /* 情報メッセージ */
        .stAlert-info {
            background-color: #F0F7FF;
            color: #004085;
            border: 1px solid #B8DAFF;
            border-radius: 8px;
        }
        
        /* エラーメッセージ */
        .stAlert-error {
            background-color: #FFF5F5;
            color: #C53030;
            border: 1px solid #FEB2B2;
            border-radius: 8px;
        }
        
        /* ラジオボタン */
        .stRadio > div {
            color: var(--text-color);
        }
        
        /* テキスト入力 */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stDateInput > div > div > input,
        .stSelectbox > div > div > div {
            border-radius: 8px;
            border: 1px solid #E0E0E0;
            transition: border-color 0.2s;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stDateInput > div > div > input:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(255, 140, 0, 0.1);
        }
        
        /* サイドバー */
        section[data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: 1px solid #E0E0E0;
        }
        
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: var(--text-color);
            border: none;
            padding-left: 0;
        }
        
        /* キャプション */
        .stCaption {
            color: #888888;
        }
        
        /* ディバイダー */
        hr {
            border: none;
            border-top: 1px solid #EEEEEE;
            margin: 20px 0;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )
    # endregion

    # --- サイドバー（設定入力） ---
    user_config = render_sidebar()

    # region --- UIモード変更時のセッション状態リセット ---
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
    # endregion

    # region --- ユーザーID変更時のセッション状態リセット ---
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
    # endregion

    # region --- ゲートウェイ層を初期化 ---
    log_gateway = CSVLogRepository(log_path="data/logs.csv")
    approval_gateway = ApprovalRepository(db_path="data/approvals.db")
    # endregion

    # region --- ユースケース層を初期化 ---
    log_usecase = Logging(log_gateway)
    config_usecase = Personalization(config_dir="personalized")
    task_usecase = ExpenseReport(log_usecase)
    # endregion

    # region --- パーソナライズ設定読込 ---
    if user_config["mode"] == UIMode.PERSONALIZE.value and user_config["user_id"]:
        st.session_state[smi.CONFIG] = config_usecase.load_config(
            user_config["user_id"]
        )
    else:
        # 固定UIの場合はCONFIGをクリア
        if smi.CONFIG in st.session_state:
            del st.session_state[smi.CONFIG]

    config = st.session_state.get(smi.CONFIG, {})
    category_order = config.get("category_order", CATEGORIES)
    font_size = config.get("font_size", 16)
    # endregion

    # region --- AI からの適用要求があればセッションにデータを反映 ---
    if st.session_state.get("apply_ai_data"):
        form_data = st.session_state.get("form_data_to_apply", {}) or {}

        # 1. カテゴリのマッピング（既に components.py で設定されている可能性が高いが念のため）
        mapped = st.session_state.get(smi.CATEGORY)
        if mapped:
            st.session_state[smi.TASK_STARTED] = True

        # 2. データの反映とキーのマッピング
        existing = st.session_state.get("loaded_submission", {}) or {}
        merged = {**existing, **form_data}
        st.session_state["loaded_submission"] = merged

        if mapped == CAT_BUSINESS_TRIP:
            # 出張精算用のキー名への変換マップ
            field_map = {
                "destination": "destination_trip",
                "departure": "departure_trip",
                "arrival": "arrival_trip",
                "amount": "amount_trip",
                "date": "date_from",
                "purpose": "purpose_trip",
                "car_name": "car_name_trip",
                "car_number": "car_number_trip",
                "transportation": "transportation_trip",
                "is_roundtrip": "is_roundtrip_trip",
            }
            for k, v in merged.items():
                target_key = field_map.get(k, k)
                st.session_state[target_key] = v
                logging.info(
                    f"Applied AI data to session_state (mapped): {target_key} = {v}"
                )
        else:
            for k, v in merged.items():
                st.session_state[k] = v
                logging.info(f"Applied AI data to session_state: {k} = {v}")

        st.session_state["apply_ai_data"] = False
        st.rerun()
    # endregion

    # region --- メインUI ---
    st.title("💼 経費精算システム（実験用）")

    # region CSS 動的生成
    font_css = f"""
        <style>
        html, body, [class*="css"], .stMarkdown, .stButton, .stInput, .stSelectbox, .stTextArea, p, span, div, li {{
            font-size: {font_size}px !important;
        }}
        h1 {{ font-size: {font_size * 1.5}px !important; }}
        h2 {{ font-size: {font_size * 1.3}px !important; }}
        h3 {{ font-size: {font_size * 1.1}px !important; }}
        </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)
    # endregion

    # region モード表示
    if user_config["mode"] == UIMode.PERSONALIZE.value:
        mode_badge = "🎨 パーソナライズUI"
        mode_color = "#FF8C00"
    else:
        mode_badge = "📋 固定UI"
        mode_color = "#666666"

    st.markdown(
        f"<div style='text-align: center; padding: 10px; border: 1px solid {mode_color}44; background: {mode_color}11; border-radius: 8px; margin-bottom: 20px;'><span style='color: {mode_color}; font-weight: bold;'>{mode_badge}</span></div>",
        unsafe_allow_html=True,
    )
    # endregion

    colA, colB = st.columns([5, 2])

    with colA:

        # region --- 新規申請 ---
        st.subheader("📝 新規申請")

        # 申請完了メッセージを表示
        if st.session_state.get("submission_success"):
            st.markdown(
                f"<div style='background: #FFF4E5; color: #663C00; padding: 15px; border-radius: 8px; border-left: 5px solid #FF8C00; margin-bottom: 15px;'><span style='font-size: 18px;'>✅ {st.session_state['submission_success']}</span></div>",
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
                "<div style='background: #FFF4E5; padding: 12px; border-radius: 8px; margin-bottom: 15px; border-left: 3px solid #FF8C00;'><span style='color: #FF8C00; font-weight: bold;'>⭐ よく使う区分から追加</span></div>",
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

        # endregion

        # region --- 最近の申請履歴セクション（パーソナライズUIのみ） ---
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
                                        f"<span style='color: #FF8C00; font-weight: bold;'>{cat_icon} {category}</span> - {data.get('destination', 'N/A')}",
                                        unsafe_allow_html=True,
                                    )
                                    st.caption(
                                        f"💰 金額: ¥{data.get('amount', 0):,} | 往復: {'はい' if data.get('is_roundtrip') else 'いいえ'} | 📅 {dt_str}"
                                    )
                                elif category == CAT_BUSINESS_TRIP:
                                    st.markdown(
                                        f"<span style='color: #FF8C00; font-weight: bold;'>{cat_icon} {category}</span> - {data.get('destination', 'N/A')}",
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
                                        f"<span style='color: #FF8C00; font-weight: bold;'>{cat_icon} {category}</span>",
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
                        "<div style='background: #F8F9FA; padding: 15px; border-radius: 8px; border-left: 4px solid #DEE2E6;'>ℹ️ 申請履歴がありません</div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 4px solid #FF8C00;'>ℹ️ ユーザーIDを入力して開始してください</div>",
                    unsafe_allow_html=True,
                )
        # endregion
    with colB:
        # 右側サマリを表示
        render_summary(category_order, BUTTONS_BASE, config, user_config["mode"])

        # region --- AI チャットパネル表示 ---
        # パーソナライズUI のときは右カラム内に AI チャットを表示
        if user_config["mode"] == UIMode.PERSONALIZE.value:
            try:
                ai_agent = AIAgent()
                render_ai_chat_panel(
                    ai_agent,
                    user_config.get("user_id", ""),
                    approval_gateway,
                    config_usecase,
                )
            except Exception as e:
                # AI 初期化に失敗してもメイン処理は継続
                logger = logging.getLogger(__name__)
                logger.warning("AI panel initialization failed: %s", e)
        # endregion
    # endregion


if __name__ == "__main__":
    run_app()
