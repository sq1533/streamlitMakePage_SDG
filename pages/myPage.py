import streamlit as st
import utils
import time

# 회원 로그인 구분
if "userID" not in st.session_state:
    st.session_state.userID = False

# 회원 허용 유무
if "userAllow" not in st.session_state:
    st.session_state.userAllow = False

# 고객 주소 정보
if "address" not in st.session_state:
    st.session_state.address = '배송지 입력하기'

st.markdown(
    """
    <style>
    div[aria-label="dialog"][role="dialog"] {
        width: 80% !important;
        max-width: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 비밀번호 변경

# 배송지 추가
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
# 배송지 삭제

if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.title(body="마이페이지")
        signOut = st.button(
            label="회원탈퇴",
            key="signOut",
            type="primary",
            use_container_width=True
        )
        if signOut:
            st.switch_page(page="pages/signOut.py")

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

        email, passward = st.columns(spec=[2,1], gap="small", vertical_alignment="bottom")
        email.text_input(
            label="Email",
            value=st.session_state.user["email"],
            key="myinfoEmail",
            type="default",
            disabled=True
        )
        passwardBTN = passward.button(
            label="비밀번호 변경",
            key="myinfoPWbtn",
            type="primary",
            use_container_width=True
        )
        if passwardBTN:
            st.switch_page(page="pages/myPageChangePW.py")
        st.text_input(
            label="이름",
            value=st.session_state.user["name"],
            key="myinfoName",
            type="default",
            disabled=True
        )
        st.text_input(
            label="휴대폰 번호",
            value=st.session_state.user["phone"],
            key="myinfoPhone",
            type="default",
            disabled=True
        )
        for address in st.session_state.user["address"]:
            addr, deleteB, empty = st.columns(spec=[3,1,2], gap="small", vertical_alignment="center")
            addr.markdown(body=f"###### {address}")
            deleteBTN = deleteB.button(
                label="삭제",
                key=f"delete_{address}",
                type="secondary",
                use_container_width=False
                )
            if deleteBTN:
                deleteAddress(address=address)
        addAddress = st.text_input(
            label="추가 주소지",
            key="myinfoAddAddress",
            type="default"
        )
        addAddressBTN = st.button(
            label="배송지 검색",
            key="myinfoAddress",
            type="primary",
            use_container_width=True
        )
        if addAddressBTN:
            addressPOP(addAddress)
            #if st.session_state.user["address"].__len__() <= 5:
            #    addressPOP(addAddress)
            #else:
            #    st.warning(body="등록 가능한 주소지는 5개입니다.")