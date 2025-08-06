import streamlit as st
import utils
from datetime import datetime, timezone, timedelta
import time
import requests

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = False

st.markdown(
    body="""
    <style>
    button[data-testid="stBaseButton-elementToolbar"][aria-label="Fullscreen"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 80% !important;
        max-width: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not st.session_state.userID:
    st.switch_page(page="mainPage.py")
else:

    userInfo = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).get().val()

    with st.sidebar:
        st.title(body="주문내역")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label="홈으로 이동",
            key="goHomeFromOrderPage",
            type="primary",
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")
        
        st.markdown(body="주문 내역")
        if userInfo.get('orderList') == None:
            st.markdown(body="아직 주문내역이 없습니다.")
        else:
            orderList = [i for i in userInfo.get('orderList').values()]
            for order in reversed(orderList):
                # 주문 정보
                orderTime = order.get('time')
                itemID = order.get('item')
                address = order.get('address')
                status = order.get('status')

                # 아이템 정보
                itemInfo = utils.database().pyrebase_db_items.child(itemID).get().val()

                with st.exception(exception=f'주문 시간 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemInfo.get('name')} {status}'):
                    itemImage, itemInfo = st.columns(spec=2, gap="small", vertical_alignment="center")
                orderImage.image(
                    image=itemInfo.get("paths")[0],
                    caption=None,
                    use_container_width=True,
                    clamp=False,
                    output_format="auto"
                    )
                orderInfo.markdown(
                    body=f"상품명 : {itemInfo.get('name')} // 주문 날짜 : {orderTime}"
                    )
                if "/cancel" in order:
                    orderStatus.markdown(body="취소")
                    cancel.button(
                        label="취소 완료",
                        key=f"cancel_{order}_complete",
                        type="secondary",
                        use_container_width=True,
                        disabled=True
                    )
                elif "/delivery" in order:
                    orderStatus.markdown(body="배송중")
                    cancelBTN = cancel.button(
                        label="취소 요청하기",
                        key=f"cancel_{order}_request",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)
                elif "/complete" in order:
                    orderStatus.markdown(body="배송 완료")
                    cancelBTN = cancel.button(
                        label="교환/환불",
                        key=f"return_{order}",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)
                else:
                    orderStatus.markdown(body="상품 준비중")
                    cancelBTN = cancel.button(
                        label="취소",
                        key=f"cancel_{order}",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)