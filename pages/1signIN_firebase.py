import streamlit as st
import userFunc.userAuth as userAuth
import time

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
# 회원 로그인 구분
if 'uid' not in st.session_state:
    st.session_state.uid = None
# 로그인 시도
if 'allowCount' not in st.session_state:
    st.session_state.allowCount = 0

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
    st.switch_page(page='mainPage.py')
else:
    with st.sidebar:
        st.title(body='Email 로그인')

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

        ID = st.text_input(
            label='email',
            value='',
            max_chars=40,
            key='userID',
            type='default',
            placeholder='email@email.com',
            disabled=False,
            label_visibility='hidden',
            width='stretch'
        )
        PW = st.text_input(
            label='password',
            value='',
            max_chars=80,
            key='userPW',
            type='password',
            placeholder='비밀번호',
            disabled=False,
            label_visibility='hidden',
            width='stretch'
        )
        # firebase 이메일 로그인
        signINB = st.button(
            label='signIN',
            key='firebaseSignIN',
            type="primary",
            use_container_width=True
        )
        if (ID and PW) or signINB:
            signINuser = userAuth.guest.signIN(id=ID, pw=PW)
            if st.session_state.allowCount <= 7:
                if signINuser['allow']:
                    st.session_state.uid = signINuser['uid']
                    st.session_state.user = signINuser['result']
                    st.rerun()
                else:
                    st.session_state.allowCount += 1
                    st.warning(body=signINuser['result'])
            else:
                with st.spinner(text='비정상 로그인 시도, 10초 비활성화', show_time=True):
                    time.sleep(10)
                    st.session_state.allowCount = 0
                    st.switch_page(page='mainPage.py')