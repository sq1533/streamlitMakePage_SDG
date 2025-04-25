import streamlit as st
from firebase_admin import auth

# sidebar Nav 기능 비활성화
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 홈으로 이동
goHome = st.button(
    label="홈으로 이동",
    key="goHome",
    type="primary",
    use_container_width=False,
    disabled=False
)
if goHome:
    st.switch_page(page="mainPage.py")

# 사용자 정보 입력
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "email" not in st.query_params:
    st.query_params.email = None
if "solt" not in st.query_params:
    st.query_params.solt = None

auth.get_user_by_phone_number