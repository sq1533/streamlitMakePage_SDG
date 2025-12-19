import streamlit as st
import utils
import api
import time
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO - 교환 요청',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

utils.init_session()

def clearOrderItem():
    st.session_state.orderItem = None

# 교환 요청 dialog
@st.dialog(title='교환 요청', width='medium')
def exchangeCall(key : str, item : str):
    st.markdown(body='### 교환 요청을 진행하시겠습니까?')
    st.warning(
        body="""
        안내\n
        동일한 상품으로 교환이 진행됩니다.
        상품 회수 완료 및 검수 후 새 상품이 발송됩니다.
        재고 부족 시 교환이 불가능할 수 있으며, 이 경우 별도 안내 후 환불 처리됩니다.
        """
        )

    empty, exchange = st.columns(spec=[3,1], gap='small', vertical_alignment='center')
    exchangeB = exchange.button(
        label='교환 요청하기',
        type='primary'
    )
    if exchangeB:
        func : bool = api.items.orderExchange(token=st.session_state.token, key=key, itemID=item)
        if func:
            st.info(body='교환 요청 완료, 주문내역으로 이동합니다.')
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            st.button(label='잠시만 기다려주세요...', on_click=clearOrderItem, type='tertiary', disabled=True)
            st.session_state.orderItem = None
            st.rerun()
        else:
            st.warning(body='교환 요청 실패, 다시 시도해주세요.')

# 회원 로그인 검증 및 주문 상품 정보 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.orderItem:
    with st.sidebar:
        st.title(body="교환 요청")

    # 홈으로 이동
    goHome = st.button(
        label='HOME',
        type='primary',
        width='content',
        disabled=False
    )
    if goHome:
        st.switch_page(page="mainPage.py")

    key = st.session_state.orderItem[0]
    orderInfo = st.session_state.orderItem[1]

    itemID = orderInfo.get('item')
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

        empty, exchangeItem = st.columns(spec=[2,1], gap='small', vertical_alignment='center')
        exchangeItemB = exchangeItem.button(
            label='교환 요청하기',
            type='primary',
            width='stretch'
        )
        if exchangeItemB:
            exchangeCall(key=key, item=itemID)
else:
    st.switch_page(page='pages/3myPage_orderList.py')
