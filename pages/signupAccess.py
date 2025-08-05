import streamlit as st
import time
import utils

# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = False

# 가입 이메일 정보
if "password" not in st.session_state:
    st.session_state.password = False

# 세션 검증 및 이메일 검증
if st.session_state.signup_step:
    with st.sidebar:
        st.title("환영합니다.")

    user = utils.database().pyrebase_auth.sign_in_with_email_and_password(email=st.session_state.signup_email, password=st.session_state.password)
    sendResult = utils.guest.sendEmail(userToken=user['idToken'])

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
                st.session_state.clear
                st.rerun()
else:
    st.switch_page(page="mainPage.py")