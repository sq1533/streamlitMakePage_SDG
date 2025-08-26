import streamlit as st
import time
import utils

# 회원 가입 구분
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = False

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
            label='HOME',
            key='goHOME',
            type='primary',
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

            if email:
                with st.spinner(text="이메일을 확인해볼게요", show_time=True):
                    try:
                        userEmail = utils.guest.emailCK(id=email)
                        if userEmail['allow']: # 신규 회원일 경우
                            checkEmail = st.button(
                                label="다음",
                                key="goMakePW",
                                type="primary",
                                use_container_width=True
                            )
                            if checkEmail:
                                st.session_state.signup_email = email
                                st.switch_page(page="pages/signupPW.py")
                        else:
                            st.error(
                                body=userEmail['result']
                            )
                    except Exception as e:
                        print(e)
                        st.error(
                            body=e
                        )
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")