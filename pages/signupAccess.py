import streamlit as st
from firebase_admin import auth

from signup import solt

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

if st.query_params.signupStep == st.session_state.signup_email and st.query_params.solt == solt:
    st.write("올바른 접근")
elif st.query_params.signupStep == st.session_state.signup_email and st.query_params.solt != solt:
    st.write("솔트 정보 오류")
else:
    st.write("오류")