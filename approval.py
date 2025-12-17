import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from datetime import datetime
from infrastructure.approvalRepository import ApprovalRepository
from domain.constants import CAT_TRNSPORTS, CAT_BUSINESS_TRIP


def render_submission_details(submission: dict):
    """申請詳細を表示"""
    data = submission["data"]
    category = submission["category"]

    cat_icon = (
        "🚗" if category == "交通費精算" else "✈️" if category == "出張精算" else "📋"
    )

    st.markdown(
        f"<div style='background: linear-gradient(90deg, #2E86AB22, #A23B7222); padding: 15px; border-radius: 8px; margin-bottom: 20px;'><h3 style='color: #2E86AB; margin: 0;'>{cat_icon} 申請詳細: {category}</h3></div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"<span style='color: #2E86AB; font-weight: bold;'>👤 申請者:</span> {data.get('user', 'N/A')}",
            unsafe_allow_html=True,
        )
    with col2:
        submitted_at = datetime.fromisoformat(submission["submitted_at"]).strftime(
            "%Y年%m月%d日 %H:%M"
        )
        st.markdown(
            f"<span style='color: #2E86AB; font-weight: bold;'>📅 申請日時:</span> {submitted_at}",
            unsafe_allow_html=True,
        )
    with col3:
        status_color = (
            "#06A77D"
            if submission["status"] == "承認"
            else "#D62828" if submission["status"] == "却下" else "#F18F01"
        )
        st.markdown(
            f"<span style='color: {status_color}; font-weight: bold;'>🏷️ ステータス:</span> <span style='color: {status_color};'>{submission['status']}</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    # カテゴリに応じた詳細表示
    if category == "交通費精算":
        st.markdown(
            "<div style='background: #2E86AB11; padding: 15px; border-radius: 8px;'><h4 style='color: #2E86AB; margin-top: 0;'>🚗 交通費申請内容</h4>",
            unsafe_allow_html=True,
        )
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>📅 日付:</span> {data.get('date', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🎯 目的地:</span> {data.get('destination', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>📍 出発:</span> {data.get('departure', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🏁 到着:</span> {data.get('arrival', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🔄 往復:</span> {'はい' if data.get('is_roundtrip') else 'いいえ'}",
                unsafe_allow_html=True,
            )
        with col_r:
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💰 金額:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('amount', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💵 合計金額:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('total', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🚙 車名:</span> {data.get('car_name', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🔢 ナンバー:</span> {data.get('car_number', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #2E86AB; font-weight: bold;'>🚌 交通機関:</span> {data.get('transportation', 'N/A')}",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<span style='color: #2E86AB; font-weight: bold;'>📝 交通目的:</span> {data.get('purpose', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color: #2E86AB; font-weight: bold;'>📄 領収書:</span> {'✅ あり' if data.get('uploaded_file') else '❌ なし'}",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    elif category == "出張精算":
        st.markdown(
            "<div style='background: #A23B7211; padding: 15px; border-radius: 8px;'><h4 style='color: #A23B72; margin-top: 0;'>✈️ 出張申請内容</h4>",
            unsafe_allow_html=True,
        )
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>📅 出張期間:</span> {data.get('date_from', 'N/A')} ～ {data.get('date_to', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>🌍 出張先:</span> {data.get('destination', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>📍 出発:</span> {data.get('departure', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>🏁 到着:</span> {data.get('arrival', 'N/A')}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>🔄 往復:</span> {'はい' if data.get('is_roundtrip') else 'いいえ'}",
                unsafe_allow_html=True,
            )
        with col_r:
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💰 交通費:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('amount', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💵 合計交通費:</span> <span style='font-size: 18px; color: #06A77D;'>¥{data.get('total', 0):,}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>📋 日当日数:</span> {data.get('allowance_day', 0)}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>💷 日当金額:</span> ¥{data.get('daily_allowance', 0):,}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #A23B72; font-weight: bold;'>🏨 宿泊日数:</span> {data.get('accommodation_day', 0)}",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span style='color: #06A77D; font-weight: bold;'>🏩 宿泊費用:</span> ¥{data.get('accommodation_fee', 0):,}",
                unsafe_allow_html=True,
            )
        st.markdown(
            f"<span style='color: #A23B72; font-weight: bold;'>🚙 車名:</span> {data.get('car_name', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color: #A23B72; font-weight: bold;'>🔢 ナンバー:</span> {data.get('car_number', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color: #A23B72; font-weight: bold;'>🚌 交通機関:</span> {data.get('transportation', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color: #A23B72; font-weight: bold;'>📝 出張目的:</span> {data.get('purpose', 'N/A')}",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<span style='color: #A23B72; font-weight: bold;'>📄 領収書:</span> {'✅ あり' if data.get('uploaded_file') else '❌ なし'}",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # 合計金額を計算して表示
        total_cost = (
            data.get("amount", 0)
            + data.get("allowance_day", 0) * data.get("daily_allowance", 0)
            + data.get("accommodation_day", 0) * data.get("accommodation_fee", 0)
        )
        st.markdown(
            f"<div style='background: linear-gradient(90deg, #06A77D22, #06A77D44); padding: 15px; border-radius: 8px; text-align: center; margin-top: 15px;'><h4 style='color: #06A77D; margin: 0;'>💰 合計申請額: ¥{total_cost:,}</h4></div>",
            unsafe_allow_html=True,
        )


def run_approval_app():
    st.set_page_config(page_title="申請承認", layout="wide")

    # CSS スタイル定義
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
        
        h1 {
            background: linear-gradient(90deg, #2E86AB, #A23B72);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        h2 {
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            padding-bottom: 10px;
        }
        
        h3 {
            color: #A23B72;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            background: linear-gradient(90deg, #2E86AB, #1F5A7F);
            color: white;
            border-radius: 8px 8px 0 0;
            padding: 10px 20px;
            font-weight: bold;
            border: none;
        }
        
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            background: linear-gradient(90deg, #A23B72, #7A1955);
            box-shadow: 0 4px 8px rgba(162, 59, 114, 0.3);
        }
        
        .stButton > button {
            background: linear-gradient(90deg, #2E86AB, #1F5A7F);
            color: white;
            border: none;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(46, 134, 171, 0.4);
        }
        
        .stTextArea textarea {
            border-radius: 8px;
            border: 2px solid #2E86AB;
        }
        
        .stTextArea textarea:focus {
            border-color: #A23B72;
            box-shadow: 0 0 0 0.2rem rgba(162, 59, 114, 0.25);
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
            "<h3 style='color: #2E86AB; border-bottom: 3px solid #2E86AB; padding-bottom: 10px;'>⏳ 未承認申請</h3>",
            unsafe_allow_html=True,
        )
        pending_submissions = approval_repo.get_pending_submissions()

        if not pending_submissions:
            st.markdown(
                "<div style='background: #F1800122; padding: 15px; border-radius: 8px; border-left: 4px solid #F18F01;'>ℹ️ 未承認の申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #2E86AB11; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>📊 全 <span style='color: #2E86AB; font-weight: bold;'>{len(pending_submissions)}</span> 件の未承認申請</div>",
                unsafe_allow_html=True,
            )

            col_list, col_detail = st.columns([1, 2])

            with col_list:
                st.markdown(
                    "<h4 style='color: #2E86AB;'>📋 申請一覧</h4>",
                    unsafe_allow_html=True,
                )
                selected_idx = None
                for i, submission in enumerate(pending_submissions):
                    category = submission["category"]
                    user = submission["data"].get("user", "Unknown")
                    submitted_at = datetime.fromisoformat(
                        submission["submitted_at"]
                    ).strftime("%m/%d %H:%M")

                    cat_icon = "🚗" if category == "交通費精算" else "✈️"
                    btn_text = f"{cat_icon} {category}\n👤 {user}\n⏰ {submitted_at}"

                    if st.button(
                        btn_text,
                        key=f"pending_{i}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_submission_id"] = submission["id"]

            with col_detail:
                selected_id = st.session_state.get("selected_submission_id")
                if selected_id:
                    submission = approval_repo.get_submission_by_id(selected_id)
                    if submission:
                        render_submission_details(submission)

                        st.divider()

                        col_approve, col_reject = st.columns(2)

                        with col_approve:
                            if st.button(
                                "✅ 承認",
                                key="approve_btn",
                                use_container_width=True,
                                type="primary",
                            ):
                                approval_repo.approve_submission(selected_id, "admin")
                                st.success("申請を承認しました")
                                del st.session_state["selected_submission_id"]
                                st.rerun()

                        with col_reject:
                            if st.button(
                                "❌ 却下",
                                key="reject_btn",
                                use_container_width=True,
                                type="secondary",
                            ):
                                st.session_state["show_reject_reason"] = True

                        if st.session_state.get("show_reject_reason"):
                            st.divider()
                            st.write("### 却下理由の入力")
                            reason = st.text_area(
                                "却下理由を入力してください",
                                key="reject_reason_input",
                                height=100,
                                placeholder="例：金額が不正です、領収書が不足しています など",
                            )
                            col_confirm, col_cancel = st.columns(2)
                            with col_confirm:
                                if st.button(
                                    "却下を確定",
                                    key="confirm_reject_btn",
                                    use_container_width=True,
                                    type="primary",
                                ):
                                    if reason.strip():
                                        approval_repo.reject_submission(
                                            selected_id, reason
                                        )
                                        st.success("申請を却下しました")
                                        del st.session_state["selected_submission_id"]
                                        st.session_state["show_reject_reason"] = False
                                        st.rerun()
                                    else:
                                        st.error("却下理由を入力してください")

                            with col_cancel:
                                if st.button(
                                    "キャンセル",
                                    key="cancel_reject_btn",
                                    use_container_width=True,
                                ):
                                    st.session_state["show_reject_reason"] = False
                                    st.rerun()
                else:
                    st.info("申請を選択してください")

    with tab2:
        st.markdown(
            "<h3 style='color: #06A77D; border-bottom: 3px solid #06A77D; padding-bottom: 10px;'>✅ 承認済申請</h3>",
            unsafe_allow_html=True,
        )
        approved_submissions = approval_repo.get_all_submissions(status="approved")

        if not approved_submissions:
            st.markdown(
                "<div style='background: #F1800122; padding: 15px; border-radius: 8px; border-left: 4px solid #F18F01;'>ℹ️ 承認済の申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #06A77D11; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>📊 全 <span style='color: #06A77D; font-weight: bold;'>{len(approved_submissions)}</span> 件の承認済申請</div>",
                unsafe_allow_html=True,
            )

            for submission in approved_submissions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        cat_icon = "🚗" if category == "交通費精算" else "✈️"
                        st.markdown(
                            f"<span style='color: #2E86AB; font-weight: bold;'>{cat_icon} {category}</span> - {user}",
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

    with tab3:
        st.markdown(
            "<h3 style='color: #D62828; border-bottom: 3px solid #D62828; padding-bottom: 10px;'>❌ 却下申請</h3>",
            unsafe_allow_html=True,
        )
        rejected_submissions = approval_repo.get_all_submissions(status="rejected")

        if not rejected_submissions:
            st.markdown(
                "<div style='background: #F1800122; padding: 15px; border-radius: 8px; border-left: 4px solid #F18F01;'>ℹ️ 却下された申請はありません</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='background: #D6282833; padding: 10px; border-radius: 8px; margin-bottom: 15px;'>📊 全 <span style='color: #D62828; font-weight: bold;'>{len(rejected_submissions)}</span> 件の却下申請</div>",
                unsafe_allow_html=True,
            )

            for submission in rejected_submissions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        cat_icon = "🚗" if category == "交通費精算" else "✈️"
                        st.markdown(
                            f"<span style='color: #2E86AB; font-weight: bold;'>{cat_icon} {category}</span> - {user}",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"📅 {submitted_at}")
                        if submission.get("rejection_reason"):
                            st.markdown(
                                f"<div style='background: #D6282822; padding: 8px; border-radius: 4px; margin-top: 5px;'><span style='color: #D62828; font-weight: bold;'>❌ 却下理由:</span> {submission['rejection_reason']}</div>",
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


if __name__ == "__main__":
    run_approval_app()
