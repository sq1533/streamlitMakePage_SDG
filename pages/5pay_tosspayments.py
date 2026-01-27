import streamlit as st
import utils
import api
import time
import streamlit.components.v1 as components
from api.tosspay_widget import render_payment_widget
from api.tosspay_handler import handle_payment_callback
from datetime import datetime, timezone

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)

# 페이지 UI 변경 사항
utils.set_page_ui()

utils.init_session()

if 'orderNo' not in st.session_state:
    st.session_state.orderNo = None

toss_secret_key = st.secrets["tosspayments"]["secret_key"]
toss_client_key = st.secrets["tosspayments"]["client_key"]

if any(value is not None for value in st.session_state.token.values()) and st.session_state.item and st.session_state.orderNo:
    itemInfo = api.items.showItem().loc[st.session_state.item]
    orderNo = st.session_state.orderNo

    render_payment_widget(
        client_key=toss_client_key,
        customer_key=st.session_state.user.get('email'), 
        amount=int(itemInfo['price']),
        order_id=orderNo,
        order_name=itemInfo['name'],
        customer_email=st.session_state.user.get('email'),
        customer_name=st.session_state.user.get('name', '고객'),
        success_url="https://amuredo.shop/tosspayment_success", 
        fail_url="https://amuredo.shop/tosspayment_fail",
        height=1000
    )
    if st.button("⬅️ 뒤로 가기 (주문 취소)"):
        api.items.cancelReservation(token=st.session_state.token, itemID=st.session_state.item, orderTime=st.session_state.orderNo[:12])
        st.switch_page("pages/5orderPage.py")

else:
    st.error("잘못된 접근입니다.")
    st.switch_page("mainPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)