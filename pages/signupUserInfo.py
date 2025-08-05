import streamlit as st
import utils
import time
from datetime import datetime, timezone, timedelta


# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = False

# 가입 이메일 정보
if "password" not in st.session_state:
    st.session_state.password = False

# 고객 주소 정보
if "address" not in st.session_state:
    st.session_state.address = '배송지 입력하기'

now = datetime.now(timezone.utc) + timedelta(hours=9)
nowDay = now.strftime('%Y-%m-%d')

@st.dialog(title='주소 검색')
def addrDialog():
    dialogAddr = st.text_input(
        label="주소",
        value=None,
        key="addrTrue",
        type="default",
        disabled=False
    )
    if dialogAddr == None:
        st.markdown(
            body="검색창에 찾을 주소를 입력해주세요."
        )
    else:
        for i in utils.seachAddress(dialogAddr):
            addrNo, addrStr, btn = st.columns(spec=[1,4,1], gap='small', vertical_alignment='center')
            addrNo.markdown(
                body=list(i.keys())[0]
            )
            addrStr.markdown(
                body=list(i.values())[0]
            )
            choice = btn.button(
                label="선택",
                key=list(i.values())[0],
                type="primary",
                use_container_width=False
            )
            if choice:
                st.session_state.address = list(i.keys())[0] + ' ' + list(i.values())[0]
                st.rerun()
        return st.session_state.address

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
        addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='center')
        addr = st.text_input(
            label="기본 배송지",
            value=st.session_state.address,
            key="addrNone",
            type="default",
            disabled=True
        )
        searchAddr = st.button(
            label="찾아보기",
            key="addressSearch",
            type="primary",
            use_container_width=False
        )
        if searchAddr:
            addrDialog()

        detailAddr = st.text_input(
            label="상세주소",
            value="",
            key="detailAddr",
            type="default"
        )
        
        address = st.session_state.address + ' ' + detailAddr

        infomation = {
            'email':st.session_state.signup_email,
            'name':name,
            'phoneNumber':phone,
            'address':[address],
            'createPW':nowDay
        }

        sendEmail = st.button(
            label="인증 메일 보내기",
            key="done",
            type="primary",
            use_container_width=True
        )
        if sendEmail:
            if name == None or phone == None or detailAddr == "상세주소 입력하기" or st.session_state.address == '배송지 입력하기':
                st.error(body="아직 완료되지 않았어요.")
            else:
                try:
                    endStep = utils.guest.signUP(
                        id=st.session_state.signup_email,
                        pw=st.session_state.password,
                        userInfo=infomation
                        )
                    if endStep:
                        st.info(body="인증 메일을 보내는 중이에요.")
                        time.sleep(2)
                        st.switch_page(page="pages/signupAccess.py")
                    else:
                        st.warning(body="입력하신 정보에 오류가 있어요. 확인해주세요")
                        time.sleep(3)
                        st.rerun()
                except Exception:
                    st.error(body=f"회원가입 실패")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")