import streamlit as st
import utils
import time
from datetime import datetime, timezone, timedelta


# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = None

# 가입 이메일 정보
if "password" not in st.session_state:
    st.session_state.password = None

now = datetime.now(timezone.utc) + timedelta(hours=9)

if st.session_state.signup_step:
    with st.sidebar:
        st.title("환영합니다.")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        st.progress(
            value=66,
            text="거의 다 왔어요~!"
        )
        name = st.text_input(
            label="이름",
            value=None,
            key="userName",
            type="default"
        )
        phone = st.text_input(
            label="전화번호",
            value=None,
            key="userPhone",
            type="default"
        )
        addr = st.text_input(
            label="주소 찾아보기",
            value=None,
            key="searchAddr",
            type="default"
        )
        searchAddr = st.button(
            label="검색",
            key="addressSearch",
            type="primary",
            use_container_width=False
        )
        if searchAddr:
            @st.dialog(title='주소 검색')
            def test(ad):
                return utils.seachAddress(address=ad)
        detailAddr = st.text_input(
            label="상세주소",
            value=None,
            key="detailAddr",
            type="default"
        )
        st.session_state.address = test(ad=addr) + detailAddr

        signupDone = st.button(
            label="회원가입 완료",
            key="done",
            type="primary",
            use_container_width=True
        )
        if signupDone:
            if name == None or phone == None or st.session_state.address == None:
                st.error(body="아직 완료되지 않았어요.")
            else:
                try:
                    auth.update_user(
                        uid=st.session_state.uid,
                        disabled=False
                    )
                    userInfo = {
                        "id" : st.session_state.uid,
                        "createPW" : now.strftime("%Y-%m-%d"),
                        "email" : auth.get_user_by_uid(uid=st.session_state.uid).email,
                        "name" : name,
                        "phone" : phone,
                        "address" : [st.session_state.address],
                        "like" : [],
                        "orders" : []
                    }
                    userConn.document(st.session_state.uid).set(userInfo)
                    st.info(body="회원가입이 완료되었습니다.")
                    time.sleep(2)
                    st.switch_page(page="mainPage.py")
                except Exception:
                    st.error(body=f"회원가입 실패")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")