import streamlit as st
import userFunc.userAuth as userAuth
import time

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'firebase':None,
        'naver':None,
        'kakao':None,
        'gmail':None
    }
# 회원 정보 세션
if 'user' not in st.session_state:
    st.session_state.user = None

# 상세 주소 선택 구분
if 'selectAddr' not in st.session_state:
    st.session_state.selectAddr = None

st.html(
    """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

# 주소 세션 추기
def addrSession(addr : str):
    st.session_state.selectAddr = addr

# 배송지 추가
@st.dialog(title='주소 검색', width='large')
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
            st.markdown(body=f'### {st.session_state.selectAddr}')

            detailAddress = st.text_input(
                label='상세주소',
                key='myInfoDetailAddr',
                type='default'
            )
            addAddrToFirebase = st.button(
                label='추가하기',
                key='addAddrFirebase',
                type='primary',
                use_container_width=True
            )
            if addAddrToFirebase:
                newAddr = st.session_state.selectAddr + ' ' + detailAddress
                userAuth.guest.addAddr(token=st.session_state.token, addAddr=newAddr)
                st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
                st.session_state.selectAddr = None
                st.rerun()
        else:
            if userAuth.seachAddress(dialogAddr)['allow']:
                for i in userAuth.seachAddress(dialogAddr)['result']:
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
                st.session_state.selectAddr = None
                st.warning(body=userAuth.seachAddress(dialogAddr)['result'])
    else:
        st.session_state.selectAddr = None
        st.markdown(body="검색창에 찾을 주소를 입력해주세요.")

# 페이지
if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title(body="마이페이지")
        signOut = st.button(
            label="회원탈퇴",
            key="signOut",
            type="primary",
            use_container_width=True
        )
        if signOut:
            st.switch_page(page="pages/5-2signOut.py")

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

        if userAuth.guest.showEmailVerified(token=st.session_state.token):

            email, passward = st.columns(spec=[2,1], gap="small", vertical_alignment="bottom")

            email.text_input(
                label='email',
                value=st.session_state.user.get('email'),
                key='myInfoEmail',
                type='default',
                disabled=True
            )
            passwardBTN = passward.button(
                label='비밀번호 변경',
                key='myInfoPW',
                type='primary',
                use_container_width=True
            )

            if passwardBTN:
                st.switch_page(page="pages/3myPage_changePW.py")

            st.text_input(
                label='이름',
                value=st.session_state.user.get('name'),
                key='myInfoName',
                type='default',
                disabled=True
            )

            st.text_input(
                label='휴대폰 번호',
                value=st.session_state.user.get('phoneNumber'),
                key='myInfoPhone',
                type='default',
                disabled=True
            )

            st.markdown(body='##### 주 배송지')
            st.markdown(body=f"###### {st.session_state.user.get('address')['home']}")

            st.markdown(body='##### 주소 리스트')
            for key, address in st.session_state.user.get('address').items():
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
                        userAuth.guest.delAddr(
                            token=st.session_state.token,
                            delAddrKey=key
                            )
                        del st.session_state.user['address'][key]
                        st.rerun()

                    homeAddrBTN = homeAddrB.button(
                        label="주 배송지로 변경",
                        key=f"home_{key}",
                        type="secondary",
                        use_container_width=False
                        )
                    if homeAddrBTN:
                        userAuth.guest.homeAddr(
                            token=st.session_state.token,
                            homeAddrKey=key,
                            homeAddr=address
                        )
                        st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
                        st.rerun()

            addAddressBTN = st.button(
                label='배송지 추가',
                key='myInfoAddAddr',
                type='primary',
                use_container_width=True
            )
            if addAddressBTN:
                if st.session_state.user.get('address').__len__() >= 4:
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
                sent = userAuth.guest.sendEmail(userMail=st.session_state.user.get('email'))
                if sent:
                    st.info(body='인증메일을 전송했어요. 메일함을 확인해주세요.')
                    time.sleep(2)
                    st.session_state.clear()
else:
    st.switch_page(page="mainPage.py")