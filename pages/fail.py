import streamlit as st
import time

st.markdown(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.error("이메일 인증 실패")
time.sleep(2)
st.switch_page(page="mainPage.py")