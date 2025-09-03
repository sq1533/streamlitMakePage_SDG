import streamlit as st
import utils
import time
from datetime import datetime

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
        width: 75% !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 배송지 변경 dialog
@st.dialog(title='배송지 변경')
def changeAddr(key : str):
    addrDict = utils.guest.showUserInfo(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'])['result']['address']
    result = st.selectbox(
        label='주소 선택',
        options=addrDict.values(),
        key='cgAddr_select'
    )
    empty, btn = st.columns(spec=[4,1], gap='small', vertical_alignment='center')
    goBtn = btn.button(
        label='확인',
        key=f'cgAddr_check',
        type='primary',
        use_container_width=True
    )
    if goBtn:
        func = utils.items.cgAddr(
            uid=st.session_state.user['localId'],
            token=st.session_state.user['idToken'],
            key=key,
            addr=result
            )
        if func:
            st.info(body='배송지 변경 완료, 주문내역으로 이동합니다.')
            time.sleep(2)
            st.switch_page(page='pages/myPageOrderList.py')
        else:
            st.warning(body='배송지 변경 실패, 다시 시도해주세요.')

if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:
    if not st.session_state.orderItem:
        st.switch_page(page="mainPage.py")
    else:
        with st.sidebar:
            st.title(body="배송지 변경")

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

            showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료'
            }

            st.markdown(body="배송지 변경 요청")

            key = st.session_state.orderItem[0]
            orderInfo = st.session_state.orderItem[1]
            
            orderTime = key
            itemID = orderInfo.get('item')
            address = orderInfo.get('address')
            status = showStatus[orderInfo.get('status')]

            # 아이템 정보
            itemInfo = utils.items.itemInfo(itemId=itemID)['result']

            with st.container(height=250, border=True, key='changeAddress'):
                image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                image.image(
                    image=itemInfo.get("paths")[0],
                    caption=None,
                    clamp=False,
                    output_format="auto"
                    )
                info.markdown(
                    body=f"""
                    상품명 : {itemInfo.get('name')}\n\n
                    주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')}\n\n
                    주문 상태 : {status}\n\n
                    {address}
                    """
                    )

            empty, cgAddr = st.columns(spec=[2,1], gap='small', vertical_alignment='center')
            changeAddrB = cgAddr.button(
                label='배송지 변경',
                key=f'cgAddr_{key}',
                type='primary',
                use_container_width=True
            )
            if changeAddrB:
                changeAddr(key=key)