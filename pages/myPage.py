import streamlit as st
import utils
import time

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False

# 회원 이메일 인증 확인
if "emailCK" not in st.session_state:
    st.session_state.emailCK = False

# 상세 주소 선택 구분
if "selectAddr" not in st.session_state:
    st.session_state.selectAddr = None


st.markdown(
    """
    <style>
    div[aria-label="dialog"][role="dialog"] {
        width: 75% !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 주소 세션 추기
def addrSession(addr : str):
    st.session_state.selectAddr = addr

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
            if addAddrToFirebase:
                newAddr = st.session_state.selectAddr + ' ' + detailAddress
                utils.guest.addAddr(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'], addAddr=newAddr)
                st.session_state.selectAddr = None
                st.rerun()
        else:
            if utils.seachAddress(dialogAddr)['allow']:
                for i in utils.seachAddress(dialogAddr)['result']:
                    addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')
                    addrNo.markdown(
                        body=i
                    )
                    btn.button(
                        label="선택",
                        key=i,
                        on_click=addrSession(i),
                        type="primary",
                        use_container_width=True
                    )
            else:
                st.warning(
                    body=utils.seachAddress(dialogAddr)['result']
                )
                st.session_state.selectAddr = None
    else:
        st.session_state.selectAddr = None
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

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label="HOME",
            key="goHome",
            type="primary",
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        if st.session_state.emailCK:
            # 사용자 정보 불러오기
            userInfo = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).get(token=st.session_state.user['idToken']).val()

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
            addrLen = userInfo.get('address').__len__()
            st.markdown(body='##### 주 배송지')
            st.markdown(body=f"###### {userInfo.get('address')['home']}")

            st.markdown(body='##### 주소 리스트')
            if addrLen != 1:
                for key, address in userInfo.get('address').items():
                    if key == 'home':
                        pass
                    else:
                        st.markdown(body=f"###### {address}")
                        empty, homeAddrB, deleteB,  = st.columns(spec=[3,2,1], gap="small", vertical_alignment="center")
                        deleteBTN = deleteB.button(
                            label="삭제",
                            key=f"delete_{key}",
                            type="secondary",
                            use_container_width=False
                            )
                        if deleteBTN:
                            utils.guest.delAddr(
                                uid=st.session_state.user['localId'],
                                token=st.session_state.user['idToken'],
                                delAddr=key
                                )
                            st.rerun()
                        homeAddrBTN = homeAddrB.button(
                            label="주 배송지로 변경",
                            key=f"home_{key}",
                            type="secondary",
                            use_container_width=False
                            )
                        if homeAddrBTN:
                            utils.guest.homeAddr(
                                uid=st.session_state.user['localId'],
                                token=st.session_state.user['idToken'],
                                addr=address,
                                delAddr=key
                            )
                            st.rerun()
                        
            else:
                pass

            addAddressBTN = st.button(
                label="배송지 검색",
                key="myinfoAddress",
                type="primary",
                use_container_width=True
            )
            if addAddressBTN:
                if userInfo.get('address').__len__() >= 4:
                    st.warning(body="추가 등록할 수 없습니다.")
                else:
                    addrDialog()
        else:
            st.warning(body='이메일 인증이 완료되지 않았습니다. 이메일 인증을 진행해주세요.')
            sendEmail = st.button(
                label="이메일 인증 보내기",
                key="sendEmail",
                type="primary",
                use_container_width=True
            )
            if sendEmail:
                sent = utils.guest.sendEmail(token=st.session_state.user['idToken'])
                if sent:
                    st.info(body='인증메일을 전송했어요. 메일함을 확인해주세요.')
                    time.sleep(2)
                    st.session_state.clear()