import time

import streamlit as st

from usecases.logging import Logging
from presentation.const import UIMode, SessionManagementItems as smi


class ExpenseReport:
    def __init__(self, logging_usecase: Logging):
        self.logging_usecase = logging_usecase

    def start_task(self):
        self.start_time = time.time()
        self.logging_usecase.add_event(
            st.session_state[smi.USER_ID],
            st.session_state[smi.MODE],
            "button",
            "task_start",
            "start",
            None,
            True,
        )
        st.session_state[smi.TASK_STARTED] = True

    def add_event(self, event, action="", value="", success=True):
        self.logging_usecase.add_event(
            st.session_state[smi.USER_ID],
            st.session_state[smi.MODE],
            event,
            st.session_state[smi.CATEGORY],
            action,
            value,
            success,
        )

    def get_top_rejection_reasons(self, approval_repo, limit: int = 3):
        """却下理由のTOP Nを取得する"""
        return approval_repo.get_top_rejection_reasons(limit=limit)

    def get_top_rejection_reasons_by_user(
        self, approval_repo, user_id: str, limit: int = 3
    ):
        """ユーザーごとの却下理由のTOP Nを取得する"""
        return approval_repo.get_top_rejection_reasons_by_user(user_id, limit=limit)
