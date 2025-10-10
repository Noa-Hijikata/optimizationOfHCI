import streamlit as st


def render_sidebar():
    """サイドバー設定を描画し、ユーザー設定を返す"""
    st.sidebar.header("実験設定")

    mode = st.sidebar.radio("UIモード", ["固定UI", "パーソナライズUI"])
    user_id = st.sidebar.text_input("被験者ID（必須）")
    period = st.sidebar.selectbox("期間", ["2025-08", "2025-07", "2025-06"])
    project = st.sidebar.text_input("プロジェクト初期値", "A-42")

    return {"mode": mode, "user_id": user_id, "period": period, "project": project}
