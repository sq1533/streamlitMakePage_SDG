import streamlit as st
import utils

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False

# 회원 허용 유무
if "userAllow" not in st.session_state:
    st.session_state.userAllow = False

# 상세 주소 선택 구분
if "selectAddr" not in st.session_state:
    st.session_state.selectAddr = None


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
    if dialogAddr:
        if st.session_state.selectAddr:
            st.markdown(
                body=f'### {st.session_state.selectAddr}'
            )
            detailAddress = st.text_input(
                label="상세 주소지",
                key="myinfoAddAddress",
                type="default"
            )
            addAddrToFirebase = st.button(
                label="추가하기",
                key="addrToFirebase",
                type="primary",
                use_container_width=True
            )
            if detailAddress or addAddrToFirebase:
                newAddr = st.session_state.selectAddr + detailAddress
                utils.guest.addAddr(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'], addAddr=newAddr)
                st.session_state.selectAddr = None
                st.rerun()
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
                    st.session_state.selectAddr = f'{list(i.keys())[0]} {list(i.values())[0]}'
    else:
        st.markdown(
            body="검색창에 찾을 주소를 입력해주세요."
        )

# 페이지
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

    # 사용자 정보 불러오기
    userInfo = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).get(token=st.session_state.user['idToken']).val()

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
            value=userInfo.get('email'),
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
            value=userInfo.get('name'),
            key="myinfoName",
            type="default",
            disabled=True
        )
        st.text_input(
            label="휴대폰 번호",
            value=userInfo.get('phoneNumber'),
            key="myinfoPhone",
            type="default",
            disabled=True
        )
        
        st.markdown(body=f"###### {userInfo.get('address')[0]} 주 배송지")

        for address in userInfo.get('address')[1:]:
            addr, deleteB, empty = st.columns(spec=[3,1,2], gap="small", vertical_alignment="center")
            addr.markdown(body=f"###### {address}")
            deleteBTN = deleteB.button(
                label="삭제",
                key=f"delete_{address}",
                type="secondary",
                use_container_width=False
                )
            if deleteBTN:
                utils.guest.delAddr(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'], delAddr=address)
                st.rerun()

        addAddressBTN = st.button(
            label="배송지 검색",
            key="myinfoAddress",
            type="primary",
            use_container_width=True
        )

        if addAddressBTN:
            if userInfo.get('address').__len__() > 5:
                st.warning(body="등록 가능한 주소지는 5개입니다.")
            else:
                addrDialog()