import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import datetime
from infrastructure.approvalRepository import ApprovalRepository
from domain.constants import CAT_TRNSPORTS, CAT_BUSINESS_TRIP


def render_submission_details(submission: dict, approval_repo):
    """申請詳細を表示し、承認/却下アクションを行う"""
    data = submission["data"]
    category = submission["category"]
    submission_id = submission["id"]

    cat_icon = (
        "🚗" if category == "交通費精算" else "✈️" if category == "出張精算" else "📋"
    )

    st.markdown(
        f"<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 5px solid #FF8C00; margin-bottom: 20px;'><h3 style='color: #FF8C00; margin: 0;'>{cat_icon} 申請詳細: {category} (ID: {submission_id})</h3></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<span style='color: #FF8C00; font-weight: bold;'>👤 申請者:</span> {data.get('user', 'N/A')}",
            unsafe_allow_html=True,
        )
    with col2:
        submitted_at = datetime.fromisoformat(submission["submitted_at"]).strftime(
            "%Y年%m月%d日 %H:%M"
        )
        st.markdown(
            f"<span style='color: #FF8C00; font-weight: bold;'>📅 申請日時:</span> {submitted_at}",
            unsafe_allow_html=True,
        )

    st.divider()

    # カテゴリに応じた詳細表示
    if category == "交通費精算":
        st.markdown(
            "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 3px solid #FF8C00;'><h4 style='color: #FF8C00; margin-top: 0;'>🚗 交通費申請内容</h4>",
            unsafe_allow_html=True,
        )
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>📅 日付:</span> {data.get('date', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🎯 目的地:</span> {data.get('destination', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>📍 出発:</span> {data.get('departure', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🏁 到着:</span> {data.get('arrival', 'N/A')}",
                unsafe_allow_html=True,
            )
        with col_r:
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💰 金額:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('amount', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🚙 車名:</span> {data.get('car_name', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🚌 交通機関:</span> {data.get('transportation', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🔄 往復:</span> {'はい' if data.get('is_roundtrip') else 'いいえ'}",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<span style='color: #FF8C00; font-weight: bold;'>📝 交通目的:</span> {data.get('purpose', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    elif category == "出張精算":
        st.markdown(
            "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 3px solid #FF8C00;'><h4 style='color: #FF8C00; margin-top: 0;'>✈️ 出張申請内容</h4>",
            unsafe_allow_html=True,
        )
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>📅 出張期間:</span> {data.get('date_from', 'N/A')} ～ {data.get('date_to', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>🌍 出張先:</span> {data.get('destination', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #FF8C00; font-weight: bold;'>📍 出発:</span> {data.get('departure', 'N/A')}",
                unsafe_allow_html=True,
            )
        with col_r:
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💰 交通費:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('amount', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💷 日当金額:</span> ¥{data.get('daily_allowance', 0):,}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>🏩 宿泊費用:</span> ¥{data.get('accommodation_fee', 0):,}",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<span style='color: #FF8C00; font-weight: bold;'>📝 出張目的:</span> {data.get('purpose', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        total_cost = (
            data.get("amount", 0)
            + data.get("allowance_day", 0) * data.get("daily_allowance", 0)
            + data.get("accommodation_day", 0) * data.get("accommodation_fee", 0)
        )
        st.markdown(
            f"<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #FF8C00; margin-top: 15px;'><h4 style='color: #FF8C00; margin: 0;'>💰 合計申請額: ¥{total_cost:,}</h4></div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # 承認・却下アクション
    if submission["status"] == "pending":
        col_approve, col_reject = st.columns(2)

        with col_approve:
            if st.button("✅ 承認確定", use_container_width=True, type="primary"):
                approval_repo.approve_submission(submission_id, "admin")
                st.success("申請を承認しました")
                st.rerun()

        with col_reject:
            if st.button("❌ 却下", use_container_width=True):
                st.session_state["show_reject_input"] = True

        if st.session_state.get("show_reject_input"):
            st.markdown("---")
            reason = st.text_area(
                "却下理由を入力してください", key="modal_reject_reason"
            )
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("却下を確定", use_container_width=True, type="primary"):
                    if reason.strip():
                        approval_repo.reject_submission(submission_id, reason)
                        st.success("申請を却下しました")
                        st.session_state["show_reject_input"] = False
                        st.rerun()
                    else:
                        st.error("理由を入力してください")
            with col_c2:
                if st.button("キャンセル", use_container_width=True):
                    st.session_state["show_reject_input"] = False
                    st.rerun()
    else:
        status_color = "#06A77D" if submission["status"] == "approved" else "#D62828"
        status_text = "✅ 承認済" if submission["status"] == "approved" else "❌ 却下"
        st.markdown(
            f"<div style='text-align: center; padding: 15px; background: {status_color}11; border: 1px solid {status_color}; border-radius: 8px;'><h4 style='color: {status_color}; margin: 0;'>{status_text}</h4></div>",
            unsafe_allow_html=True,
        )
        if submission.get("rejection_reason"):
            st.info(f"却下理由: {submission['rejection_reason']}")


@st.dialog("📝 申請詳細確認・判定", width="large")
def show_submission_modal(submission_id, approval_repo):
    """申請詳細をモーダル（st.dialog）で表示"""
    submission = approval_repo.get_submission_by_id(submission_id)
    if submission:
        render_submission_details(submission, approval_repo)
    else:
        st.error("申請データが見つかりませんでした。")


def run_approval_app():
    st.set_page_config(page_title="申請承認", layout="wide")

    # CSS スタイル定義
    st.markdown(
        """
        <style>
        :root {
            --primary-color: #FF8C00;
            --secondary-color: #555555;
            --accent-color: #FFA500;
            --success-color: #06A77D;
            --danger-color: #D62828;
            --background-color: #FFFFFF;
        }
        
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
        
        h2 {
            color: #262730;
            border-left: 4px solid var(--primary-color);
            padding-left: 12px;
            margin-top: 25px;
            font-weight: 600;
            border-bottom: none;
        }
        
        h3, h4 {
            color: #262730;
            border-left: 4px solid var(--primary-color);
            padding-left: 12px;
            margin-top: 15px;
            font-weight: 600;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            color: #555555;
            padding: 10px 20px;
            font-weight: bold;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            color: var(--primary-color);
            border-bottom: 2px solid var(--primary-color);
        }
        
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s ease;
        }
        
        .stButton > button:hover {
            background: #E67E00;
            box-shadow: 0 4px 8px rgba(255, 140, 0, 0.3);
            transform: translateY(-1px);
        }
        
        .stTextArea textarea {
            border-radius: 8px;
            border: 1px solid #E0E0E0;
        }
        
        .stTextArea textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px rgba(255, 140, 0, 0.1);
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("📋 申請承認システム")

    # DB を初期化
    approval_repo = ApprovalRepository(db_path="data/approvals.db")

    # --- タブで切り替え ---
    tab1, tab2, tab3 = st.tabs(["⏳ 未承認", "✅ 承認済", "❌ 却下"])

    with tab1:
        st.markdown(
            "<h3>⏳ 未承認申請</h3>",
            unsafe_allow_html=True,
        )
        pending_submissions = approval_repo.get_pending_submissions()

        if not pending_submissions:
            st.markdown(
                "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 4px solid #FF8C00;'>ℹ️ 未承認の申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #FFF4E5; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #FF8C00;'><span style='color: #FF8C00; font-weight: bold;'>📊 未承認: {len(pending_submissions)} 件</span></div>",
                unsafe_allow_html=True,
            )

            st.markdown(
                "<h4>📋 申請一覧</h4>",
                unsafe_allow_html=True,
            )
            for i, submission in enumerate(pending_submissions):
                category = submission["category"]
                user = submission["data"].get("user", "Unknown")
                submitted_at = datetime.fromisoformat(
                    submission["submitted_at"]
                ).strftime("%m/%d %H:%M")

                cat_icon = "🚗" if category == "交通費精算" else "✈️"
                btn_text = f"{cat_icon} {category} | 👤 {user} | ⏰ {submitted_at}"

                if st.button(
                    btn_text,
                    key=f"pending_{i}",
                    use_container_width=True,
                ):
                    show_submission_modal(submission["id"], approval_repo)

    with tab2:
        st.markdown(
            "<h3>✅ 承認済申請</h3>",
            unsafe_allow_html=True,
        )
        approved_submissions = approval_repo.get_all_submissions(status="approved")

        if not approved_submissions:
            st.markdown(
                "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 4px solid #FF8C00;'>ℹ️ 承認済の申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #FFF4E5; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #06A77D;'><span style='color: #06A77D; font-weight: bold;'>📊 承認済: {len(approved_submissions)} 件</span></div>",
                unsafe_allow_html=True,
            )

            for i, submission in enumerate(approved_submissions):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        cat_icon = "🚗" if category == "交通費精算" else "✈️"
                        st.markdown(
                            f"<span style='color: #FF8C00; font-weight: bold;'>{cat_icon} {category}</span> - {user}",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"📅 {submitted_at}")
                    with col2:
                        st.markdown(
                            f"<span style='color: #666;'>ID:</span> {submission['id']}",
                            unsafe_allow_html=True,
                        )
                    with col3:
                        st.markdown(
                            f"<span style='background: #06A77D33; color: #06A77D; padding: 4px 8px; border-radius: 4px;'>✅ 承認済</span>",
                            unsafe_allow_html=True,
                        )
                    with col4:
                        if st.button(
                            "詳細", key=f"apprv_{i}", use_container_width=True
                        ):
                            show_submission_modal(submission["id"], approval_repo)

    with tab3:
        st.markdown(
            "<h3>❌ 却下申請</h3>",
            unsafe_allow_html=True,
        )
        rejected_submissions = approval_repo.get_all_submissions(status="rejected")

        if not rejected_submissions:
            st.markdown(
                "<div style='background: #FFF4E5; padding: 15px; border-radius: 8px; border-left: 4px solid #FF8C00;'>ℹ️ 却下された申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #FFF4E5; padding: 10px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #D62828;'><span style='color: #D62828; font-weight: bold;'>📊 却下: {len(rejected_submissions)} 件</span></div>",
                unsafe_allow_html=True,
            )

            for i, submission in enumerate(rejected_submissions):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 0.8])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        cat_icon = "🚗" if category == "交通費精算" else "✈️"
                        st.markdown(
                            f"<span style='color: #FF8C00; font-weight: bold;'>{cat_icon} {category}</span> - {user}",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"📅 {submitted_at}")
                        if submission.get("rejection_reason"):
                            st.markdown(
                                f"<div style='background: #D6282811; padding: 8px; border-radius: 4px; border-left: 3px solid #D62828; margin-top: 5px;'><span style='color: #D62828; font-weight: bold;'>❌ 却下理由:</span> {submission['rejection_reason']}</div>",
                                unsafe_allow_html=True,
                            )
                    with col2:
                        st.markdown(
                            f"<span style='color: #666;'>ID:</span> {submission['id']}",
                            unsafe_allow_html=True,
                        )
                    with col3:
                        st.markdown(
                            f"<span style='background: #D6282833; color: #D62828; padding: 4px 8px; border-radius: 4px;'>❌ 却下</span>",
                            unsafe_allow_html=True,
                        )
                    with col4:
                        if st.button("詳細", key=f"rej_{i}", use_container_width=True):
                            show_submission_modal(submission["id"], approval_repo)


if __name__ == "__main__":
    run_approval_app()
