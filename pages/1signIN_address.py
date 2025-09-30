import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth
import utils
import time

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

# 고객 주소 정보
if 'address' not in st.session_state:
    st.session_state.address = '배송지 입력하기'

# 페이지 UI 변경 사항
st.html(
    """
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
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
                    st.session_state.address = i
                    st.rerun()
        else:
            st.markdown(body="검색 실패, 다시 시도해주세요.")

if any(value is not None for value in st.session_state.token.values()):
        with st.sidebar:
            st.title(body='기본 배송지 설정')

        empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

        with main.container():
            addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

            addr.text_input(
                label="기본 배송지",
                value=st.session_state.address,
                key="addrNone",
                type="default",
                disabled=True
            )

            searchAddrB = searchAddr.button(
                label="찾아보기",
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

            # 최종 주소지
            address = st.session_state.address + ' ' + detailAddr

            conditionMain, conditionBox = st.columns(spec=[6,1], gap='small', vertical_alignment='top')
            infoUsedMain, infoUsedBox = st.columns(spec=[6,1], gap='small', vertical_alignment='top')

            with conditionMain.expander(label='[필수] 이용약관 동의'):
                st.text(body=utils.database().condition)

            condtion = conditionBox.checkbox(
                label='동의',
                key='conditionAgree'
            )

            with infoUsedMain.expander(label='[필수] 개인정보 이용 동의'):
                st.html(body=utils.database().infoUsed)

            infoUsed = infoUsedBox.checkbox(
                label='동의',
                key='usedAgree'
            )
            if st.session_state.address != '배송지 입력하기' and detailAddr and condtion and infoUsed:
                addAddrB = st.button(
                    label='기본 배송지 설정하기',
                    key='baseAddr',
                    type='primary',
                    use_container_width=True
                )
                if addAddrB:
                    result = userAuth.guest.addHomeAddr(token=st.session_state.token, addr=address)
                    if result:
                        st.info(body='기본 배송지 설정 완료, 메인페이지 이동중 ..')
                        st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
                        time.sleep(2)
                        st.switch_page(page='mainPage.py')
                    else:
                        st.warning(body='기본 배송지 추가 실패, 다시 시도해주세요.')
else:
    st.switch_page(page='mainPage.py')