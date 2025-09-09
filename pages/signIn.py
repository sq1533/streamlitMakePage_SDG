import streamlit as st
import utils

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = None
if "userInfo" not in st.session_state:
    st.session_state.userInfo = None

st.markdown(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.markdown(f'# SIGN-IN / SIGN-UP')

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

        signUp, signIn = st.columns(spec=2, gap='small', vertical_alignment='center')

        signInB = signIn.button(
            label="signIN",
            type="primary",
            use_container_width=True
        )
        if (ID and PW) or signInB:
            goSignIn = utils.guest.signIN(id=ID, pw=PW)
            if goSignIn['allow']:
                st.session_state.user = goSignIn['result']
                st.session_state.userInfo = goSignIn['info']
                st.rerun()
            else:
                st.error(
                    body='로그인 실패, 계정정보를 확인해주세요.'
                )

        signUpB = signUp.button(
            label="회원가입",
            type="secondary",
            use_container_width=True
        )
        if signUpB:
            st.session_state.signup_step = True
            st.switch_page(page="pages/signup.py")