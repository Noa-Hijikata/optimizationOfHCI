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

    st.subheader(f"申請詳細: {category}")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**申請者:** {data.get('user', 'N/A')}")
    with col2:
        submitted_at = datetime.fromisoformat(submission["submitted_at"]).strftime(
            "%Y年%m月%d日 %H:%M"
        )
        st.write(f"**申請日時:** {submitted_at}")
    with col3:
        st.write(f"**ステータス:** {submission['status']}")

    st.divider()

    # カテゴリに応じた詳細表示
    if category == "交通費精算":
        st.write("### 交通費申請内容")
        col_l, col_r = st.columns(2)
        with col_l:
            st.write(f"**日付:** {data.get('date', 'N/A')}")
            st.write(f"**目的地:** {data.get('destination', 'N/A')}")
            st.write(f"**出発:** {data.get('departure', 'N/A')}")
            st.write(f"**到着:** {data.get('arrival', 'N/A')}")
            st.write(f"**往復:** {'はい' if data.get('is_roundtrip') else 'いいえ'}")
        with col_r:
            st.write(f"**金額:** ¥{data.get('amount', 0):,}")
            st.write(f"**合計金額:** ¥{data.get('total', 0):,}")
            st.write(f"**車名:** {data.get('car_name', 'N/A')}")
            st.write(f"**ナンバー:** {data.get('car_number', 'N/A')}")
            st.write(f"**交通機関:** {data.get('transportation', 'N/A')}")
        st.write(f"**交通目的:** {data.get('purpose', 'N/A')}")
        st.write(f"**領収書:** {'あり' if data.get('uploaded_file') else 'なし'}")

    elif category == "出張精算":
        st.write("### 出張申請内容")
        col_l, col_r = st.columns(2)
        with col_l:
            st.write(
                f"**出張期間:** {data.get('date_from', 'N/A')} ～ {data.get('date_to', 'N/A')}"
            )
            st.write(f"**出張先:** {data.get('destination', 'N/A')}")
            st.write(f"**出発:** {data.get('departure', 'N/A')}")
            st.write(f"**到着:** {data.get('arrival', 'N/A')}")
            st.write(f"**往復:** {'はい' if data.get('is_roundtrip') else 'いいえ'}")
        with col_r:
            st.write(f"**交通費:** ¥{data.get('amount', 0):,}")
            st.write(f"**合計交通費:** ¥{data.get('total', 0):,}")
            st.write(f"**日当日数:** {data.get('allowance_day', 0)}")
            st.write(f"**日当金額:** ¥{data.get('daily_allowance', 0):,}")
            st.write(f"**宿泊日数:** {data.get('accommodation_day', 0)}")
            st.write(f"**宿泊費用:** ¥{data.get('accommodation_fee', 0):,}")
        st.write(f"**車名:** {data.get('car_name', 'N/A')}")
        st.write(f"**ナンバー:** {data.get('car_number', 'N/A')}")
        st.write(f"**交通機関:** {data.get('transportation', 'N/A')}")
        st.write(f"**出張目的:** {data.get('purpose', 'N/A')}")
        st.write(f"**領収書:** {'あり' if data.get('uploaded_file') else 'なし'}")

        # 合計金額を計算して表示
        total_cost = (
            data.get("amount", 0)
            + data.get("allowance_day", 0) * data.get("daily_allowance", 0)
            + data.get("accommodation_day", 0) * data.get("accommodation_fee", 0)
        )
        st.write(f"### 合計申請額: ¥{total_cost:,}")


def run_approval_app():
    st.set_page_config(page_title="申請承認", layout="wide")

    st.title("申請承認画面")

    # DB を初期化
    approval_repo = ApprovalRepository(db_path="data/approvals.db")

    # --- タブで切り替え ---
    tab1, tab2, tab3 = st.tabs(["未承認", "承認済", "却下"])

    with tab1:
        st.subheader("未承認申請")
        pending_submissions = approval_repo.get_pending_submissions()

        if not pending_submissions:
            st.info("未承認の申請はありません")
        else:
            st.write(f"全 {len(pending_submissions)} 件の未承認申請")

            col_list, col_detail = st.columns([1, 2])

            with col_list:
                st.write("### 申請一覧")
                selected_idx = None
                for i, submission in enumerate(pending_submissions):
                    category = submission["category"]
                    user = submission["data"].get("user", "Unknown")
                    submitted_at = datetime.fromisoformat(
                        submission["submitted_at"]
                    ).strftime("%m/%d %H:%M")

                    if st.button(
                        f"{category}\n{user}\n({submitted_at})",
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
        st.subheader("承認済申請")
        approved_submissions = approval_repo.get_all_submissions(status="approved")

        if not approved_submissions:
            st.info("承認済の申請はありません")
        else:
            st.write(f"全 {len(approved_submissions)} 件の承認済申請")

            for submission in approved_submissions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        st.write(f"**{category}** - {user} ({submitted_at})")
                    with col2:
                        st.write(f"ID: {submission['id']}")
                    with col3:
                        st.write("✅ 承認済")

    with tab3:
        st.subheader("却下申請")
        rejected_submissions = approval_repo.get_all_submissions(status="rejected")

        if not rejected_submissions:
            st.info("却下された申請はありません")
        else:
            st.write(f"全 {len(rejected_submissions)} 件の却下申請")

            for submission in rejected_submissions:
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        category = submission["category"]
                        user = submission["data"].get("user", "Unknown")
                        submitted_at = datetime.fromisoformat(
                            submission["submitted_at"]
                        ).strftime("%Y年%m月%d日 %H:%M")
                        st.write(f"**{category}** - {user} ({submitted_at})")
                        if submission.get("rejection_reason"):
                            st.caption(f"却下理由: {submission['rejection_reason']}")
                    with col2:
                        st.write(f"ID: {submission['id']}")
                    with col3:
                        st.write("❌ 却下")


if __name__ == "__main__":
    run_approval_app()
