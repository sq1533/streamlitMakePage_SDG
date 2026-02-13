import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
from datetime import datetime

# 배송지 변경 dialog
@st.dialog(title='배송지 변경', width='medium')
def changeAddr(key : str):
    st.selectbox(
        label='주소 선택',
        options=st.session_state.user.get('address').values(),
        key='cgAddr_select'
    )
    st.text_input(
        label='배송 요청사항',
        value=None,
        max_chars=100,
        key='delicomment',
        placeholder='배송 요청사항을 입력해주세요.'
    )

    empty, btn = st.columns(spec=[4,1], gap='small', vertical_alignment='center')

    goBtn = btn.button(
        label='확인',
        type='secondary',
        width='stretch'
    )
    if goBtn:
        func = api.items.orderAddrChange(token=st.session_state.token, key=key, addr=st.session_state.cgAddr_select, comment=st.session_state.delicomment)
        if func:
            st.info(body='배송지 변경 완료, 주문내역으로 이동합니다.')
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            st.session_state.page['orderItem'] = ''
            st.rerun()
        else:
            st.warning(body='배송지 변경 실패, 다시 시도해주세요.')

# 페이지 접근 검증
if not any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')
if st.session_state.page['orderItem'] == '':
    st.switch_page(page='pages/3myPage_orderList.py')

# 페이지 시작
with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()

st.title(body="배송지 변경 요청")

key = st.session_state.page['orderItem'][0]
orderInfo = st.session_state.page['orderItem'][1]

orderTime = key
splitID = orderInfo.get('item').split(',', 1)
itemID = splitID[0]
lensOption = splitID[1]
address = orderInfo.get('address')
status = utils.utilsDb().showStatus[orderInfo.get('status')]

# 아이템 정보
itemIF = api.items.showItem().loc[itemID]

with st.container(height='content', border=True):
    image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
    image.image(
        image=str(itemIF['paths'][0]),
        caption=None,
        clamp=False,
        output_format="auto"
        )
    info.markdown(
        body=f"""
        상품명 : {itemIF['name']}\n\n
        주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')}\n\n
        주문 상태 : {status}\n\n
        {address}
        """
        )

empty, cgAddr = st.columns(spec=[2,1], gap='small', vertical_alignment='center')

changeAddrB = cgAddr.button(
    label='배송지 변경',
    type='secondary',
    width='stretch'
)
if changeAddrB:
    changeAddr(key=key)