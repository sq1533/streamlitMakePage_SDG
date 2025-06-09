import streamlit as st
import time
from utils import auth
import smtplib
from email.message import EmailMessage
import secrets

# 세션 정의
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user_status" not in st.session_state:
    st.session_state.user_status = False
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None
    st.session_state.uid = None

# email 전송
def sendEmail(userMail: str) -> bool:
    SENDER_EMAIL = st.secrets["email_credentials"]["sender_email"]
    SENDER_APP_PASSWORD = st.secrets["email_credentials"]["sender_password"]
    SENDER_SERVER = st.secrets["email_credentials"]["smtp_server"]
    SENDER_PORT = st.secrets["email_credentials"]["smtp_port"]
    DEPLOYED_BASE_URL = st.secrets["email_credentials"]["base_url"]
    settingCode = auth.ActionCodeSettings(
        url=f"{DEPLOYED_BASE_URL}/success?email={userMail}",
        handle_code_in_app=True
    )
    link = auth.generate_email_verification_link(
        email=userMail,
        action_code_settings=settingCode
    )
    msg = EmailMessage()
    msg['Subject'] = "회원가입 이메일 인증"
    msg['From'] = SENDER_EMAIL
    msg['To'] = userMail
    msg.set_content(f"""
안녕하세요!

회원가입을 완료하려면 아래 링크를 클릭하여 이메일 주소를 인증해주세요:

{link}

이 링크는 일정 시간 후에 만료될 수 있습니다.

감사합니다.
""")
    try:
        with smtplib.SMTP(SENDER_SERVER, SENDER_PORT) as smtp_server:
            smtp_server.ehlo() # 서버에 자신을 소개
            smtp_server.starttls() # TLS 암호화 시작
            smtp_server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            smtp_server.send_message(msg)
        print(f"인증 이메일이 {userMail} 주소로 성공적으로 발송되었습니다.")
        return True
    except smtplib.SMTPAuthenticationError:
        print("오류: SMTP 인증 실패.")
        return False
    except smtplib.SMTPServerDisconnected:
        print("오류: SMTP 서버 연결 끊김.")
        return False
    except Exception as e:
        print(f"오류: 이메일 발송 중 예상치 못한 오류: {e}")
        return False

# 세션 검증 및 이메일 검증
if st.session_state.signup_step:

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        with st.sidebar:
            st.title("환영합니다.")
        st.progress(
            value=33,
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
                # 사용자 검증키 생성
                solt = secrets.token_hex(nbytes=6)+"!!"
                auth.create_user(
                    email=st.session_state.signup_email,
                    email_verified=False,
                    password=solt,
                    display_name=None,
                    photo_url=None,
                    disabled=True,
                    )
                st.session_state.uid = auth.get_user_by_email(email=st.session_state.signup_email).uid
                with st.spinner(text="인증 메일 전송 중...", show_time=True):
                    if sendEmail(userMail=st.session_state.signup_email):
                        st.button(
                            label="인증결과 확인",
                            key="checkAccessNew",
                            type="primary",
                            on_click=st.switch_page(page="pages/signupPW.py"),
                            use_container_width=True,
                            disabled=False
                        )
                    else:
                        st.button(
                            label="인증 실패",
                            key="checkAccessNewFalse",
                            type="primary",
                            on_click=st.switch_page(page="pages/fail.py"),
                            use_container_width=True,
                            disabled=False
                        )
            except Exception as e:
                st.error(f"사용자 생성 또는 메일 발송 실패: {e}")
        elif st.session_state.user_status == "unverified":
            try:
                # 사용자 검증키 생성
                solt = secrets.token_hex(nbytes=6)+"!!"
                uid = auth.get_user_by_email(email=st.session_state.signup_email).uid
                auth.update_user(
                    uid=uid,
                    password=solt
                )
                st.session_state.uid = auth.get_user_by_email(email=st.session_state.signup_email).uid
                with st.spinner(text="인증 메일 전송 중...", show_time=True):
                    if sendEmail(userMail=st.session_state.signup_email):
                        st.button(
                            label="인증결과 확인",
                            key="checkAccessAgain",
                            type="primary",
                            on_click=st.switch_page(page="pages/signupPW.py"),
                            use_container_width=True,
                            disabled=False
                        )
                    else:
                        st.button(
                            label="인증 실패",
                            key="checkAccessAgainFalse",
                            type="primary",
                            on_click=st.switch_page(page="pages/fail.py"),
                            use_container_width=True,
                            disabled=False
                        )
            except Exception as e:
                st.error(f"이메일 전송 중 오류 발생: {e}")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")