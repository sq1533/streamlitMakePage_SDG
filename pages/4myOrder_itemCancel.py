import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
st.html(
    body="""
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

import api
import time
import requests
from datetime import datetime


utils.init_session()

def clearOrderItem():
    st.session_state.orderItem = None

# 주문 취소 dialog
@st.dialog(title='주문 취소', width='medium')
def cancelOrder(key : str, itemID : str):
    st.markdown(body='주문 취소하시겠습니까?')

    empty, cancel = st.columns(spec=[4,1], gap='small', vertical_alignment='center')
    cancelB = cancel.button(
        label='주문 취소',
        type='primary',
    )
    if cancelB:
        func = api.items.orderCancel(token=st.session_state.token, key=key, itemID=itemID)
        if func:
            st.info(body='주문 취소 완료, 주문내역으로 이동합니다.')
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            st.button(label='잠시만 기다려주세요...', on_click=clearOrderItem, type='tertiary', disabled=True)
            st.session_state.orderItem = None
            st.rerun()
        else:
            st.warning(body='주문 취소 실패, 다시 시도해주세요.')

# 회원 로그인 검증 및 주문 상품 정보 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.orderItem:
    with st.sidebar:
        st.title(body="주문 취소")

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

        st.title(body="주문 취소")

        key = st.session_state.orderItem[0]
        orderInfo = st.session_state.orderItem[1]

        itemID = orderInfo.get('item')
        address = orderInfo.get('address')
        status = utils.database().showStatus[orderInfo.get('status')]

        # 아이템 정보
        itemIF = api.items.showItem().loc[itemID]
        with st.container(height=250, border=True):
            image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")

            image.image(
                image=str(itemIF['paths'][0]),
                caption=None,
                clamp=False,
                output_format='auto'
                )
            info.markdown(
                body=f"""
                상품명 : {itemIF['name']}\n\n
                주문 날짜 : {datetime.strptime(key, '%y%m%d%H%M%S')}\n\n
                주문 상태 : {status}\n\n
                {address}
                """
                )

        empty, cancelItem = st.columns(spec=[2,1], gap='small', vertical_alignment='center')

        cancelItemB = cancelItem.button(
            label='주문 취소하기',
            type='primary',
            width='stretch'
        )
        if cancelItemB:
            #requests.post()
            cancelOrder(key=key, itemID=itemID)
else:
    st.switch_page(page='pages/3myPage_orderList.py')