import streamlit as st
import time
from utils import pyrebase_auth

if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user" not in st.session_state:
    st.session_state.user = None

# 사용자 로그인
def myinfoPass(id,pw):
    try:
        pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
        return True
    except Exception:
        return False

if not st.session_state.user:
    st.error("잘못된 접근 입니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
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

        with st.sidebar:
            st.title(body="마이페이지")

        st.write("본인확인 인증")
        st.text_input(
            label="Email",
            value=st.session_state.user["email"],
            key="myinfoAccessEmail",
            type="default",
            disabled=True
        )
        PW = st.text_input(
            label="비밀번호",
            value=None,
            key="myinfoAccessPW",
            type="password",
            placeholder=None
        )
        access = st.button(
                label="인증",
                type="primary",
                use_container_width=True
            )
        if access:
            if myinfoPass(id=st.session_state.user["email"],pw=PW):
                st.switch_page(page="pages/myPage.py")
            else:
                st.error("인증 실패")