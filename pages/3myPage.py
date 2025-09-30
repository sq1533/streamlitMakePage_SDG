import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
# 회원 정보 세션
if 'user' not in st.session_state:
    st.session_state.user = None

# 상세 주소 선택 구분
if 'selectAddr' not in st.session_state:
    st.session_state.selectAddr = '배송지 입력하기'

st.html(
    """
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

# 배송지 추가하기
@st.dialog(title='주소 검색', width='large')
def addrDialog():
    dialogAddr = st.text_input(
        label="주소",
        value=None,
        key="addrTrue",
        type="default",
        disabled=False
    )
    if dialogAddr == None:
        st.markdown(body="검색창에 찾을 주소를 입력해주세요.")
    else:
        findAddr = userAuth.seachAddress(dialogAddr)
        if findAddr['allow']:
            for i in findAddr['result']:
                addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')

                addrNo.markdown(body=i)

                choice = btn.button(
                    label="선택",
                    key=i,
                    type="primary",
                    use_container_width=True
                )
                if choice:
                    st.session_state.selectAddr = i
                    st.rerun()
        else:
            st.markdown(body="검색 실패, 다시 시도해주세요.")

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
            st.switch_page(page="pages/6signOUT.py")

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
            use_container_width=True,
            disabled=True
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
        with st.expander(label='신규 배송지 등록'):

            addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

            addr.text_input(
                label="신규 배송지",
                value=st.session_state.selectAddr,
                key="addrNone",
                type="default",
                disabled=True
            )

            searchAddrB = searchAddr.button(
                label="검색",
                key="addressSearch",
                type="primary",
                use_container_width=True
            )

            if searchAddrB:
                addrDialog()

            detailAddr = st.text_input(
                label='상세주소',
                value='',
                key='detailAddr',
                type='default'
            )

            newAddr = st.session_state.selectAddr + ' ' + detailAddr

            addAddressBTN = st.button(
                label='배송지 추가',
                key='myInfoAddAddr',
                type='primary',
                use_container_width=True
            )

            if addAddressBTN:
                if st.session_state.selectAddr != '배송지 입력하기' and detailAddr:
                    if st.session_state.user.get('address').__len__() >= 4:
                        st.warning(body="추가 등록할 수 없습니다.")
                    else:
                        userAuth.guest.addAddr(token=st.session_state.token, addAddr=newAddr)
                        st.session_state.selectAddr = '배송지 입력하기'
                        st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
                        st.rerun()
                else:
                    st.warning(body='배송지 정보가 잘못 되었습니다.')
else:
    st.switch_page(page="mainPage.py")