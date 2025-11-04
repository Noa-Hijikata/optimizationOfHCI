import streamlit as st

from presentation.const import UIMode


def render_sidebar():
    """サイドバー設定を描画し、ユーザー設定を返す"""
    st.sidebar.header("実験設定")

    mode = st.sidebar.radio("UIモード", [UIMode.FIXED.value, UIMode.PERSONALIZE.value])
    user_id = st.sidebar.text_input("被験者ID（必須）")

    return {"mode": mode, "user_id": user_id}
