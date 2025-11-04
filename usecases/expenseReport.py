import time

import streamlit as st

from usecases.logging import Logging
from presentation.const import UIMode


class ExpenseReport:
    def __init__(self, logging_usecase: Logging):
        self.user_id = None
        self.start_time = None
        self.mode = None
        self.logging_usecase = logging_usecase

    def start_task(self):
        self.start_time = time.time()
        self.mode = st.session_state.mode
        self.user_id = st.session_state.user_id

    def add_event(self, event, category, action="", value="", success=True):
        print(self.mode)
        self.logging_usecase.add_event(
            self.user_id, self.mode, event, category, action, value, success
        )

    # def complete_task(self):
    #     elapsed = time.time() - (self.start_time or time.time())
    #     self.log_repo.save(self.events, elapsed)
    #     self.start_time = None
    #     return elapsed
