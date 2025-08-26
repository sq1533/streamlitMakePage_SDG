import streamlit as st
import utils
import requests

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = False

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = False

st.markdown(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 75% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)