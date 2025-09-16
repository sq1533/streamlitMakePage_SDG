import streamlit as st
import userFunc.userAuth as userAuth
import requests

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'firebase':None,
        'naver':None,
        'kakao':None,
        'gmail':None
    }

# 회원가입 진입
if 'signUP' not in st.session_state:
    st.session_state.signUP = False

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

if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')
else:
    with st.sidebar:
        st.title(body='로그인/회원가입')

    empty, main, empty = st.columns(spec=[1,4,1], gap='small', vertical_alignment='top')

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
            st.switch_page(page='mainPage.py')

        # 네이버 로그인 버튼
        st.html(
            body=f"""
            <a href="{userAuth.guest.naverSignUP()}" target="_self" style="display: inline-block; padding: 10px 20px; background-color: #03C75A; color: white; text-align: center; text-decoration: none; border-radius: 5px;">
                네이버 로그인
            </a>
            """
            )
        # 카카오 로그인 버튼
        st.html(
            body=f"""
            <a href="{userAuth.guest.kakaoSignUP()}" target="_self" style="display: inline-block; padding: 10px 20px; background-color: #03C75A; color: white; text-align: center; text-decoration: none; border-radius: 5px;">
                카카오 로그인
            </a>
            """
            )

        signUP, signIN = st.columns(spec=2, gap='small', vertical_alignment='center')

        # firebese 이메일 회원가입
        signUPB = signUP.button(
            label='회원가입',
            key='firebaseSignUP',
            type='secondary',
            use_container_width=True
        )

        # firebase 이메일 로그인
        signINB = signIN.button(
            label='email로그인',
            key='firebaseSignIN',
            type='primary',
            use_container_width=True
        )

        if signUPB:
            st.session_state.signUP = True
            st.switch_page(page='pages/2signUP.py')

        if signINB:
            st.switch_page(page='pages/1signIN_firebase.py')