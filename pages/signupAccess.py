import streamlit as st
import time

# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

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

# 세션 검증 및 이메일 검증
if st.session_state.signup_step:
    with st.sidebar:
        st.title("환영합니다.")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        st.progress(
            value=100,
            text="회원 가입 완료"
        )
        st.markdown(
            body="회원가입이 완료되었습니다. 원활한 이용을 위해 이메일 인증을 완료해 주세요."
        )
        with st.spinner(text='메인 페이지 이동중', show_time=True):
            st.session_state.clear()
            time.sleep(2)
            st.switch_page(page="mainPage.py")
else:
    st.switch_page(page="mainPage.py")