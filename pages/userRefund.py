import streamlit as st
import utils
import time
from datetime import datetime
import requests

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = False

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = False

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

# 환불 요청 dialog
@st.dialog(title='환불 요청')
def refundCall(key : str, item : str):
    st.markdown(body='### 환불 요청을 진행하시겠습니까?')
    st.warning(
        body="""
        안내\n
        상품 회수 비용을 제외한 상품 구매 비용으로 환불됩니다.
        상품 회수 완료 후 결제 회사에 취소 요청이 진행되며, 취소 요청 4~5일 뒤 환불이 완료될 예정입니다.
        """
        )

    empty, refund = st.columns(spec=[3,1], gap='small', vertical_alignment='center')
    refundB = refund.button(
        label='환불 요청하기',
        key=f'refund_check',
        type='primary',
    )
    if refundB:
        func = utils.items.orderRefund(
            uid=st.session_state.user['localId'],
            token=st.session_state.user['idToken'],
            key=key,
            itemID=item
            )
        if func:
            st.info(body='환불 요청 완료, 주문내역으로 이동합니다.')
            time.sleep(2)
            st.session_state.orderItem = False
            st.switch_page(page='pages/myPageOrderList.py')
        else:
            st.warning(body='환불 요청 실패, 다시 시도해주세요.')


if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    if not st.session_state.orderItem:
        st.switch_page(page="mainPage.py")
    else:
        with st.sidebar:
            st.title(body="환불 요청")

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

            key = st.session_state.orderItem[0]
            orderInfo = st.session_state.orderItem[1]

            itemID = orderInfo.get('item')
            address = orderInfo.get('address')
            status = utils.database().showStatus[orderInfo.get('status')]

            # 아이템 정보
            itemInfo = utils.items.itemInfo(itemId=itemID)['result']

            with st.container(height=250, border=True, key='refundItem'):
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

            empty, refundItem = st.columns(spec=[2,1], gap='small', vertical_alignment='center')
            refundItemB = refundItem.button(
                label='환불 요청하기',
                key=f'refundItem_{key}',
                type='primary',
                use_container_width=True
            )
            if refundItemB:
                #requests.post()
                refundCall(key=key, item=itemID)