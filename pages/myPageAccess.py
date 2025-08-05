import streamlit as st
import utils
import time

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False

if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.title(body="마이페이지")

    # email 정보 불러오기
    email = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).child('email').get().val()

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label="홈으로 이동",
            key="goHome",
            type="primary",
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        st.markdown(
            body="본인임을 한번 더 인증해 주세요!"
        )

        PW = st.text_input(
            label="비밀번호",
            value=None,
            key="myinfoAccessPW",
            type="password",
            placeholder=None
        )

        access = st.button(
                label="인증",
                type="primary",
                use_container_width=True
            )

        allowCount = 0
        if access:
            signIN = utils.guest.signIN(id=email, pw=PW)
            if allowCount > 5:
                st.markdown(
                    body=f"인증을 다수 실패했습니다. 로그아웃 및 메인 페이지로 이동합니다."
                )
                time.sleep(2)
                st.session_state.clear
                st.switch_page("mainPage.py")
            else:
                if signIN['allow']:
                    st.switch_page("pages/myPage.py")
                else:
                    allowCount += 1
                    st.markdown(
                        body=f"인증에 실패 했습니다. 인증 실패 {allowCount}회"
                    )