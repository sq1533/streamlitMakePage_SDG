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

# 세션 정의
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user_status" not in st.session_state:
    st.session_state.user_status = None
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None

# 사용자 정보 저장
# TODO : 사용자 정보 저장, 주소 검증 API 확인
if st.session_state.signup_step:
    st.progress(
        value=66,
        text="인증결과 확인"
    )
    st.text_input(
        label="아이디",
        value=st.session_state.signup_email,
        key="userEmail",
        type="default",
        disabled=True
    )
    # pw = st.text_input()
    # name = st.text_input()
    # phone = st.text_input()
    # address = st.text_input()
else:
    st.error("올바른 접근이 아닙니다.")