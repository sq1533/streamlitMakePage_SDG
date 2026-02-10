import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

utils.init_session()

# 회원 로그인 상태 점검
if any(value is not None for value in st.session_state.token.values()):

    with st.sidebar:
        utils.set_sidebarLogo()
        st.title(body="회원 탈퇴")

    st.title(body="회원을 탈퇴 하시겠습니까?")
    st.info(body='간편 로그인 회원의 경우, amuredo가 관리하는 정보만 삭제됩니다.\n원천사 측 연결을 해제하시면 완전히 탈퇴하실 수 있습니다.')
    NO, YES = st.columns(spec=2, gap="small", vertical_alignment="top")
    
    DontOut = NO.button(
        label='탈퇴 안하기',
        type='secondary',
        width='stretch'
    )
    out = YES.button(
        label='탈퇴하기',
        type='secondary',
        width='stretch'
    )

    if DontOut:
        st.toast("함께 해주셔서 감사합니다.", icon="😄")
        time.sleep(0.7)
        st.switch_page(page="mainPage.py")

    if out:
        api.guest.guestOUT(token=st.session_state.token)
        st.toast('그동한 함께 해주셔서 감사합니다.')
        time.sleep(0.7)
        st.session_state.clear()
        st.switch_page(page="mainPage.py")
else:
    st.switch_page(page="mainPage.py")