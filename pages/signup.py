import streamlit as st
from email_validator import validate_email, EmailNotValidError
import time
import utils

# 회원 가입 구분
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 
if "user_status" not in st.session_state:
    st.session_state.user_status = False

# 
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None

# 세션 정보 검증 및 이메일 검증
if st.session_state.signup_step:
    # 사이드바 내용
    with st.sidebar:
        st.title("환영합니다.")

    # 메인 페이지
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
            nextBTN = True
            checkEmail = st.button(
                label="다음",
                key="goMakePW",
                type="primary",
                use_container_width=True,
                disabled=nextBTN
            )
            if email:
                with st.spinner(text="이메일을 확인해볼게요", show_time=True):
                    try:
                        if validate_email(email=email, check_deliverability=True, timeout=5)['email'] == email:
                            userEmail = utils.guest.emailCheck(id=email)
                            if userEmail: # 신규 회원일 경우
                                nextBTN = False
                            else: # 회원가입 후 이메일 인증 안된경우, 회원가입 후 이메일 인증까지 완료한 경우
                                pass

                    except EmailNotValidError as e:
                        print(e)
                        st.error(
                            body='유효하지 않은 이메일 형식입니다.'
                        )

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