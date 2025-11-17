import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=':a:',
    layout='wide',
    initial_sidebar_state='auto'
)
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

import utils
import api
import time

# 회원 토큰 세션 및 정보
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

# 고객 주소 정보
if 'address' not in st.session_state:
    st.session_state.address = None

# 배송지 추가하기
@st.dialog(title='주소 검색', width='medium')
def addrDialog():
    st.text_input(
        label='주소',
        key='firstAddr',
        type='default',
        disabled=False
    )
    if st.session_state.firstAddr == None:
        st.markdown(body="검색창에 찾을 주소를 입력해주세요.")
    else:
        findAddr : dict = api.seachAddress(st.session_state.firstAddr)
        if findAddr.get('allow'):
            for i in findAddr['result']:
                addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')

                addrNo.markdown(body=i)

                choice = btn.button(
                    label='선택',
                    key=i,
                    type='primary',
                    width='stretch'
                )
                if choice:
                    st.session_state.address = i
                    st.rerun()
        else:
            st.markdown(body="검색 실패, 다시 시도해주세요.")

# 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title(body='기본 배송지 설정')

    # 기본 배송지 설정 페이지
    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

        addr.text_input(
            label='기본 배송지',
            type='default',
            disabled=True
        )

        searchAddrB = searchAddr.button(
            label='찾아보기',
            type='primary',
            width='stretch'
        )

        if searchAddrB:
            addrDialog()

        st.text_input(
            label='상세주소',
            key='detailAddr',
            type='default'
        )

        # 약관 동의 및 개인정보 이용 동의
        conditionMain, conditionBox = st.columns(spec=[6,1], gap='small', vertical_alignment='top')
        infoUsedMain, infoUsedBox = st.columns(spec=[6,1], gap='small', vertical_alignment='top')        
        with conditionMain.expander(label='[필수] 이용약관 동의'):
            st.text(body=utils.database().condition)
        with infoUsedMain.expander(label='[필수] 개인정보 이용 동의'):
            st.html(body=utils.database().infoUsed)
        condtion = conditionBox.checkbox(
            label='동의',
            key='conditionAgree'
        )
        infoUsed = infoUsedBox.checkbox(
            label='동의',
            key='usedAgree'
        )
        # 입력사항 확인 후 기본 배송지 설정
        if st.session_state.address and st.session_state.detailAddr and condtion and infoUsed:
            address = st.session_state.address + ' ' + st.session_state.detailAddr

            addAddrB = st.button(
                label='기본 배송지 설정하기',
                key='baseAddr',
                type='primary',
                width='stretch'
            )
            if addAddrB:
                result = api.guest.addHomeAddr(token=st.session_state.token, addr=address)
                if result:
                    st.info(body='기본 배송지 설정 완료, 메인페이지 이동중 ..')
                    st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)
                    time.sleep(2)
                    st.switch_page(page='mainPage.py')
                else:
                    st.warning(body='기본 배송지 추가 실패, 다시 시도해주세요.')
else:
    st.switch_page(page='mainPage.py')