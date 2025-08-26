import streamlit as st
import utils

# 회원 가입 구분
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.markdown(f'# SIGN-IN')

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

        ID = st.text_input(
            label="email",
            value=None,
            key="textID",
            type="default",
            placeholder=None
        )
        PW = st.text_input(
            label="password",
            value=None,
            key="textPW",
            type="password",
            placeholder=None
        )
        login = st.button(
            label="signIN",
            type="primary",
            use_container_width=True
        )
        signup = st.button(
            label="회원가입",
            type="secondary",
            use_container_width=True
        )
        if (ID and PW) or login:
            goSignIn = utils.guest.signIN(id=ID, pw=PW)
            if goSignIn['allow']:
                st.session_state.user = goSignIn['result']
                st.rerun()
            else:
                st.error(
                    body='로그인 실패, 계정정보를 확인해주세요.'
                )
        if signup:
            st.session_state.signup_step = True
            st.switch_page(page="pages/signup.py")