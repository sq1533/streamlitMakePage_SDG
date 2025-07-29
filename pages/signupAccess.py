import streamlit as st
import time
import utils

# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None

# 가입 이메일 정보
if "password" not in st.session_state:
    st.session_state.password = None

# 세션 검증 및 이메일 검증
if st.session_state.signup_step:
    with st.sidebar:
        st.title("환영합니다.")

    sendResult = utils.guest.sendEmail(id=st.session_state.signup_email, pw=st.session_state.password)

    if sendResult:
        empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")
        with main.container():
            st.progress(
                value=100,
                text="회원 가입 완료"
            )
            st.markdown(
                body="회원가입이 완료되었습니다. 원활한 이용을 위해 이메일 인증을 완료해 주세요."
            )
            with st.spinner(text="메인 페이지 이동중...", show_time=True):
                time.sleep(3)
                st.switch_page(page="mainPage.py")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")