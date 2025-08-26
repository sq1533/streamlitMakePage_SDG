import streamlit as st
import time
from utils import auth

if "user" not in st.session_state:
    st.session_state.user = False

if not st.session_state.user:
    st.error("잘못된 접근 입니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
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

        st.title("회원을 탈퇴 하시겠습니까?")
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
                auth.update_user(
                    uid=st.session_state.user["id"],
                    disabled=True
                )
                st.info(body="회원 탈퇴 완료")
                st.session_state.clear
                time.sleep(2)
                st.switch_page(page="mainPage.py")