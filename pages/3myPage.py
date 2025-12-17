import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

utils.init_session()

# 선택된 주소 초기화
def clear_address():
    st.session_state.selectAddr = None

# 배송지 추가하기
@st.dialog(title='주소 검색', width='medium', on_dismiss='rerun')
def addrDialog():
    st.text_input(
        label='주소',
        key='addrTrue',
        type='default',
        disabled=False
    )
    if st.session_state.addrTrue == None:
        st.markdown(body="검색창에 찾을 주소를 입력해주세요.")
    else:
        findAddr : dict = api.seachAddress(st.session_state.addrTrue)
        if findAddr.get('allow'):
            for i in findAddr.get('result'):
                addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')

                addrNo.markdown(body=i)

                choice = btn.button(
                    label='선택',
                    key=i,
                    type='primary',
                    width='content'
                )
                if choice:
                    st.session_state.selectAddr = i
                    st.rerun()
        else:
            st.markdown(body="검색 실패, 다시 시도해주세요.")

# 회원 로그인 검증
if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title(body='마이페이지')
        signOut = st.button(
            label='회원탈퇴',
            type='primary',
            width='stretch'
        )
        if signOut:
            st.switch_page(page="pages/6signOUT.py")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            type='primary',
            width='content',
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        st.text_input(
            label='email',
            value=st.session_state.user.get('email'),
            type='default',
            disabled=True
        )

        st.text_input(
            label='이름',
            value=st.session_state.user.get('name'),
            type='default',
            disabled=True
        )

        st.text_input(
            label='생년월일',
            value=st.session_state.user.get('age'),
            type='default',
            disabled=True
        )

        st.text_input(
            label='휴대폰 번호',
            value=st.session_state.user.get('phoneNumber'),
            type='default',
            disabled=True
        )

        # 고객 배송지 정보
        st.markdown(body='##### 주 배송지')
        st.markdown(body=f"###### {st.session_state.user.get('address')['home']}")

        st.markdown(body='##### 주소 리스트')
        for key, address in st.session_state.user.get('address').items():
            if key == 'home':
                pass
            else:
                st.markdown(body=f"###### {address}")
                empty, homeAddrB, deleteB = st.columns(spec=[3,2,1], gap="small", vertical_alignment="center")
                deleteBTN = deleteB.button(
                    label='삭제',
                    key=f'delete_{key}',
                    type='secondary',
                    width='content'
                    )
                if deleteBTN:
                    api.guest.delAddr(token=st.session_state.token, delAddrKey=key)
                    del st.session_state.user['address'][key]
                    st.rerun()

                homeAddrBTN = homeAddrB.button(
                    label='주 배송지로 변경',
                    key=f'home_{key}',
                    type='secondary',
                    width='content'
                    )
                if homeAddrBTN:
                    with st.spinner(text='주소 변경중...', show_time=True):
                        api.guest.homeAddr(token=st.session_state.token, homeAddrKey=key, homeAddr=address)
                        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                        st.rerun()

        # 신규 배송지 등록
        with st.expander(label='신규 배송지 등록'):

            addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

            addr.text_input(
                label='신규 배송지',
                key='selectAddr',
                type='default',
                disabled=True
            )

            searchAddrB = searchAddr.button(
                label='검색',
                type='primary',
                width='content'
            )

            if searchAddrB:
                addrDialog()

            st.text_input(
                label='상세주소',
                value=None,
                key='detailAddr',
                type='default'
            )

            addAddressBTN = st.button(
                label='배송지 추가',
                type='primary',
                width='content'
            )
            if addAddressBTN:
                if st.session_state.selectAddr and st.session_state.detailAddr:
                    newAddr = st.session_state.selectAddr + ' ' + st.session_state.detailAddr
                    if st.session_state.user.get('address').__len__() >= 4:
                        st.warning(body="추가 등록할 수 없습니다.")
                    else:
                        api.guest.addAddr(token=st.session_state.token, addAddr=newAddr)
                        st.button(label='잠시만 기다려주세요.', on_click=clear_address, type='tertiary', disabled=True)
                        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                        st.rerun()
                else:
                    st.warning(body='배송지 정보가 잘못 되었습니다.')
else:
    st.switch_page(page="mainPage.py")