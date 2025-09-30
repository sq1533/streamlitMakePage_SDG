import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

import utils
import userFunc.userAuth as userAuth
import itemFunc.itemInfo as itemInfo
import time
from datetime import datetime

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

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = None

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

# 배송지 변경 dialog
@st.dialog(title='배송지 변경', width='large')
def changeAddr(key : str):
    result = st.selectbox(
        label='주소 선택',
        options=st.session_state.user.get('address').values(),
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
        func = itemInfo.items.cgAddr(
            token=st.session_state.token,
            key=key,
            addr=result
            )
        if func:
            st.info(body='배송지 변경 완료, 주문내역으로 이동합니다.')
            st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
            time.sleep(2)
            st.session_state.orderItem = None
            st.rerun()
        else:
            st.warning(body='배송지 변경 실패, 다시 시도해주세요.')

if any(value is not None for value in st.session_state.token.values()) and st.session_state.orderItem:
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

        st.title(body="배송지 변경 요청")

        key = st.session_state.orderItem[0]
        orderInfo = st.session_state.orderItem[1]
            
        orderTime = key
        itemID = orderInfo.get('item')
        address = orderInfo.get('address')
        status = utils.database().showStatus[orderInfo.get('status')]

        # 아이템 정보
        itemIF = itemInfo.items.itemInfo()[itemID]

        with st.container(height=250, border=True, key='changeAddress'):
            image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
            image.image(
                image=itemIF.get("paths")[0],
                caption=None,
                clamp=False,
                output_format="auto"
                )
            info.markdown(
                body=f"""
                상품명 : {itemIF.get('name')}\n\n
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
else:
    st.switch_page(page='pages/3myPage_orderList.py')