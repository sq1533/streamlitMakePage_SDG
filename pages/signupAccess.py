import streamlit as st
import time
import smtplib
from email.message import EmailMessage
import secrets
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

# 이메일 인증 커스텀 설정
def sendEmail(user:str, solt:str):
    try:
        settingCode = auth.ActionCodeSettings(
            url=f"https://localhost:8502/signupAccess?signupStep={user}&solt={solt}",
            handle_code_in_app=True
        )
        auth.generate_email_verification_link(
            email=user,
            action_code_settings=settingCode
        )
    except Exception as e:
        print(e)
# 사용자 검증키 생성
solt = secrets.token_hex(nbytes=6)

# 세션 정의
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user_status" not in st.session_state:
    st.session_state.user_status = None
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None

# 세션 검증 및 이메일 검증
if st.session_state.signup_step:
    st.progress(
        value=25,
        text="이메일 인증"
    )
    st.text_input(
        label="아이디",
        value=st.session_state.signup_email,
        key="userEmail",
        type="default",
        disabled=True
    )
    if st.session_state.user_status == "not_found":
        try:
            auth.create_user(
                email=st.session_state.signup_email,
                email_verified=False,
                password=None,
                display_name=None,
                photo_url=None,
                disabled=False,
                )
            sendEmail(user=st.session_state.signup_email, solt=solt)
            with st.spinner(text="인증 메일 전송 중...", show_time=True):
                time.sleep(3)
            st.info(body="전송을 완료했습니다. 이메일을 확인해주세요.")
        except Exception as e:
            st.error(f"사용자 생성 또는 메일 발송 실패: {e}")
    elif st.session_state.user_status == "unverified":
        try:
            sendEmail(user=st.session_state.signup_email, solt=solt)
            with st.spinner(text="인증 메일 전송 중...", show_time=True):
                time.sleep(3)
            st.info(body="전송을 완료했습니다. 이메일을 확인해주세요.")
        except Exception as e:
            st.error(f"이메일 전송 중 오류 발생: {e}")
else:
    st.error("올바른 접근이 아닙니다.")