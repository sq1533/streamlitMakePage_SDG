import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth
import time

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }

st.html(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title(body="회원 탈퇴")

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

        st.title(body="회원을 탈퇴 하시겠습니까?")
        st.info(body='간편 로그인 회원의 경우, amuredo가 관리하는 정보만 삭제됩니다.\n원천사 측 연결을 해제하시면 완전히 탈퇴하실 수 있습니다.')
        NO, YES = st.columns(spec=2, gap="small", vertical_alignment="top")
        
        DontOut = NO.button(
            label="탈퇴 안하기",
            key="dontOut",
            type="secondary",
            use_container_width=True
        )
        out = YES.button(
            label="탈퇴 하기",
            key="out",
            type="primary",
            use_container_width=True
        )
        if DontOut:
            with st.spinner(text="함께 해주셔서 감사합니다. :smile:"):
                st.info(body="home으로 이동중...")
                time.sleep(2)
                st.switch_page(page="mainPage.py")
        if out:
            with st.spinner(text="그동한 함께 해주셔서 감사합니다."):
                userAuth.guest.guestOUT(token=st.session_state.token)
                st.info(body="회원 탈퇴 완료")
                time.sleep(2)
                st.session_state.clear()
                st.switch_page(page="mainPage.py")
else:
    st.switch_page(page="mainPage.py")