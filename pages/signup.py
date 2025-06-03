import streamlit as st
import time
from utils import auth

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

# 세션 정보 검증 및 이메일 검증
if st.session_state.signup_step:
    with st.sidebar:
        st.write("환영합니다.")
    if "signupStep" not in st.query_params:
        st.progress(
            value=0,
            text="이메일 입력 입력"
        )
        email = st.text_input(
            label="아이디",
            value=None,
            max_chars=40,
            key="createID",
            type="default",
            help=None,
            placeholder="id@email.com"
        )
        user_info = None
        if email:
            with st.spinner(text="이메일을 확인해볼게요", show_time=True):
                try:
                    user_info = auth.get_user_by_email(email=email)
                    if user_info.email_verified:
                        st.session_state.user_status = "verified"
                    else:
                        st.session_state.user_status = "unverified"
                except auth.UserNotFoundError:
                    st.session_state.user_status = "not_found"
                except Exception as e:
                    st.error(f"사용자 확인 중 오류 발생: {e}")
                    st.session_state.user_status = None
            # 회원 DB 검증
            if st.session_state.user_status == "verified":
                st.error("이미 가입한 이메일입니다. 확인해주세요.")
            elif st.session_state.user_status == "unverified":
                st.info("회원가입을 시도하셨군요!, 인증 메일을 전송할까요?")
                sendMail = st.button(
                    label="인증 메일 보내기",
                    key="sendMail1",
                    type="primary",
                    use_container_width=True,
                    disabled=False
                )
                if sendMail:
                    st.session_state.signup_email = email
                    st.switch_page(page="pages/signupAccess.py")
            elif st.session_state.user_status == "not_found":
                st.info("환영합니다. 인증 메일을 전송할까요?")
                sendMail = st.button(
                    label="인증 메일 보내기",
                    key="sendMail2",
                    type="primary",
                    use_container_width=True,
                    disabled=False
                )
                if sendMail:
                    st.session_state.signup_email = email
                    st.switch_page(page="pages/signupAccess.py")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")