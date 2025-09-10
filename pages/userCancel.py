import streamlit as st
import utils
import time
from datetime import datetime
import requests

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
if 'userInfo' not in st.session_state:
    st.session_state.userInfo = None

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = None

st.markdown(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 50% !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 주문 취소 dialog
@st.dialog(title='주문 취소')
def cancelOrder(key : str, itemID : str):
    st.markdown(body='주문 취소하시겠습니까?')

    empty, cancel = st.columns(spec=[4,1], gap='small', vertical_alignment='center')
    cancelB = cancel.button(
        label='주문 취소',
        key=f'cancel_check',
        type='primary',
    )
    if cancelB:
        func = utils.items.orderCancel(
            uid=st.session_state.user['localId'],
            token=st.session_state.user['idToken'],
            key=key,
            itemID=itemID
            )
        if func:
            st.info(body='주문 취소 완료, 주문내역으로 이동합니다.')
            st.session_state.userInfo = utils.guest.showUserInfo(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'])['result']
            time.sleep(2)
            st.session_state.orderItem = None
        else:
            st.warning(body='주문 취소 실패, 다시 시도해주세요.')

if st.session_state.user:
    if st.session_state.orderItem:
        with st.sidebar:
            st.title(body="주문 취소")

        empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

        with main.container():
            # 홈으로 이동
            goHome = st.button(
                label='HOME',
                key='goHOME',
                type='primary',
                use_container_width=False,
                disabled=False
            )
            if goHome:
                st.switch_page(page="mainPage.py")

            st.markdown(body="### 주문 취소")

            key = st.session_state.orderItem[0]
            orderInfo = st.session_state.orderItem[1]

            itemID = orderInfo.get('item')
            address = orderInfo.get('address')
            status = utils.database().showStatus[orderInfo.get('status')]

            # 아이템 정보
            itemInfo = utils.items.itemInfo(itemId=itemID)['result']

            with st.container(height=250, border=True, key='cancelItem'):
                image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                image.image(
                    image=itemInfo.get("paths")[0],
                    caption=None,
                    clamp=False,
                    output_format='auto'
                    )
                info.markdown(
                    body=f"""
                    상품명 : {itemInfo.get('name')}\n\n
                    주문 날짜 : {datetime.strptime(key, '%y%m%d%H%M%S')}\n\n
                    주문 상태 : {status}\n\n
                    {address}
                    """
                    )

            empty, cancelItem = st.columns(spec=[2,1], gap='small', vertical_alignment='center')
            cancelItemB = cancelItem.button(
                label='주문 취소하기',
                key=f'cancelItem_{key}',
                type='primary',
                use_container_width=True
            )
            if cancelItemB:
                #requests.post()
                cancelOrder(key=key, itemID=itemID)
    else:
        st.switch_page(page='pages/myPageOrderList.py')
else:
    st.switch_page(page="mainPage.py")