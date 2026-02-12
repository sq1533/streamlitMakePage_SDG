import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

def clear_searchAddr():
    st.session_state.searchAddr = None
def clear_addr():
    st.session_state.firstAddr = None
    st.session_state.detailAddr = None

# 배송지 추가하기
@st.dialog(title='주소 검색', width='medium')
def addrDialog():
    st.text_input(
        label='주소',
        key='searchAddr',
        type='default',
        disabled=False
    )
    if st.session_state.searchAddr == None:
        st.markdown(body="검색창에 찾을 주소를 입력해주세요.")
    else:
        findAddr : dict = api.seachAddress(st.session_state.searchAddr)
        if findAddr.get('allow'):
            for i in findAddr['result']:
                addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')

                addrNo.markdown(body=i)

                choice = btn.button(
                    label='선택',
                    key=i,
                    type='secondary',
                    width='stretch'
                )
                if choice:
                    st.session_state.firstAddr = i
                    st.button(label='선택 주소 초기화', on_click=clear_searchAddr, type='tertiary', disabled=True)
                    st.rerun()
        else:
            st.markdown(body="검색 실패, 다시 시도해주세요.")

# 페이지 진입 검증
if not any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')

# 페이지 시작
with st.sidebar:
    utils.set_sidebarLogo()
    st.title(body='기본 배송지 설정')

# 전화번호 없을 경우(gmail 로그인)
if st.session_state.user.get('phoneNumber') == '0':
    phone = st.text_input(
        label='전화번호',
        type='default'
    )
    userPhone = phone
else:
    userPhone = st.session_state.user.get('phoneNumber')

addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

addr.text_input(
    label='기본 배송지',
    value=st.session_state.firstAddr,
    type='default',
    disabled=True
)

searchAddrB = searchAddr.button(
    label='찾아보기',
    type='secondary',
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
    st.text(body=utils.utilsDb().condition)
with infoUsedMain.expander(label='[필수] 개인정보 이용 동의'):
    st.html(body=utils.utilsDb().infoUsed)
condtion = conditionBox.checkbox(
    label='동의',
    key='conditionAgree'
)
infoUsed = infoUsedBox.checkbox(
    label='동의',
    key='usedAgree'
)

# 입력사항 확인
if st.session_state.firstAddr and st.session_state.detailAddr and condtion and infoUsed:
    address = st.session_state.firstAddr + ' ' + st.session_state.detailAddr

    addAddrB = st.button(
        label='기본 배송지 설정하기',
        type='secondary',
        width='stretch'
    )
    if addAddrB:
        if st.session_state.user.get('phoneNumber') == '0':
            if userPhone:
                result = api.guest.addHomeAddr(token=st.session_state.token, addr=address, phoneNumber=userPhone)
            else:
                result = False
                st.warning(body='전화번호를 입력해주세요.')
        else:
            result = api.guest.addHomeAddr(token=st.session_state.token, addr=address)

        if result:
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            st.button(label='설정 완료.', on_click=clear_addr, type='secondary', disabled=True)
            st.switch_page(page=f"{st.session_state.page['page']}")
        else:
            st.warning(body='기본 배송지 추가 실패, 다시 시도해주세요.')

st.divider()
st.html(body=utils.utilsDb().infoAdmin)