import streamlit as st
import utils
import time

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False

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

if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.title(body="마이페이지")

    # email 정보 불러오기
    email = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).child('email').get(token=st.session_state.user['idToken']).val()

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            key='goHome',
            type='primary',
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        st.markdown(
            body="인증해 주세요!"
        )

        PW = st.text_input(
            label="비밀번호",
            value=None,
            key="myinfoAccessPW",
            type="password",
            placeholder=None
        )

        access = st.button(
                label='인증',
                key='access',
                type='primary',
                use_container_width=True
            )

        if access:
            signIN = utils.guest.signIN(id=email, pw=PW)
            if st.session_state.allowCount >= 5:
                st.markdown(
                    body=f"인증을 다수 실패했습니다. 로그아웃 및 메인 페이지로 이동합니다."
                )
                time.sleep(2)
                st.session_state.clear()
                st.rerun()
            else:
                st.session_state.allowCount += 1
                if signIN['allow']:
                    st.switch_page("pages/myPage.py")
                else:
                    st.markdown(
                        body=f"인증에 실패 했습니다. 인증 실패 {st.session_state.allowCount}회"
                    )