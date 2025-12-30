import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
from datetime import datetime

utils.init_session()

# 주문 취소 dialog
@st.dialog(title='주문 취소', width='medium')
def cancelOrder(key : str, orderInfo : dict, itemInfo):
    st.markdown(body='주문 취소하시겠습니까?')

    st.selectbox(
        label='취소사유',
        options=['단순 변심', '상품 불량', '상품과 다르게 수령', '기타'],
        index=0,
        placeholder='취소사유를 선택해주세요.',
        key='reason',
        width='stretch'
    )

    empty, cancel = st.columns(spec=[4,1], gap='small', vertical_alignment='center')
    cancelB = cancel.button(
        label='주문 취소',
        type='primary',
    )
    if cancelB:
        # 결제 수단 분류 및 결제 취소(pay)
        payWay = orderInfo.get('pay')
        if payWay == 'naver':
            pass
        elif payWay == 'kakao':
            refundResult = api.pay().refund_kakaopay(tid=orderInfo.get('payId'), amount=int(itemInfo['price']), reason=st.session_state.reason)
        elif payWay == 'toss':
            email = str(st.session_state.user.get('email')).split('@', 1)[0]
            raw_order_no = f"{key}{orderInfo.get('item')}{email}"
            orderNo = raw_order_no.ljust(35, '0')[:35]
            refundResult = api.pay().refund_tosspay(payToken=orderInfo.get('payId'), refundNo=orderNo, reason=st.session_state.reason)
        else:
            refundResult = False

        # 결제 취소 진행(firebase)
        if refundResult:
            func = api.items.orderCancel(token=st.session_state.token, key=key, itemID=orderInfo.get('item'))
            if func:
                st.info(body='주문 취소 완료, 주문내역으로 이동합니다.')
                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                if 'orderItem' in st.session_state:
                    del st.session_state.orderItem
                if 'reason' in st.session_state:
                    del st.session_state.reason
                st.rerun()
            else:
                st.warning(body='주문 취소 실패, 다시 시도해주세요.')
        else:
            st.warning(body='주문 취소 실패, 다시 시도해주세요.')

# 회원 로그인 검증 및 주문 상품 정보 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.orderItem:
    with st.sidebar:
        st.title(body="주문 취소")

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

    address = orderInfo.get('address')
    status = utils.utilsDb().showStatus[orderInfo.get('status')]

    # 아이템 정보
    itemIF = api.items.showItem().loc[orderInfo.get('item')]
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

    empty, cancelItem = st.columns(spec=[2,1], gap='small', vertical_alignment='center')

    cancelItemB = cancelItem.button(
        label='주문 취소하기',
        type='primary',
        width='stretch'
    )
    if cancelItemB:
        cancelOrder(key=key, orderInfo=orderInfo, itemInfo=itemIF)
else:
    st.switch_page(page='pages/3myPage_orderList.py')