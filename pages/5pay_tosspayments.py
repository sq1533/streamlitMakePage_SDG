import streamlit as st
import utils
import api
from urllib.parse import quote

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)

utils.set_page_ui()
utils.init_session()

if 'orderNo' not in st.session_state or not st.session_state.item:
    st.error("잘못된 접근입니다.")
    st.switch_page("mainPage.py")

toss_client_key = st.secrets["tosspayments"]["client_key"]
itemInfo = api.items.showItem().loc[st.session_state.item]
orderNo = st.session_state.orderNo
price = int(itemInfo['price'])
item_name = itemInfo['name']
user_email = st.session_state.user.get('email', 'anonymous')
user_name = st.session_state.user.get('name', '고객')

st.title("결제 준비")
st.info("준비가 완료되었습니다. 아래 버튼을 눌러 결제를 진행해주세요.")

# 결제 성공/실패 시 이동할 URL (상대 경로) - Bridge 페이지로 연결하여 Iframe 탈출 유도
success_url = "/payment_bridge?target=success" 
fail_url = "/payment_bridge?target=fail"

# 토스 페이먼츠 위젯 렌더링
api.tosspay_widget.render_payment_widget(
    client_key=toss_client_key,
    customer_key=user_email,
    amount=price,
    order_id=orderNo,
    order_name=item_name,
    customer_name=user_name,
    customer_email=user_email,
    success_url=success_url,
    fail_url=fail_url
)

st.divider()

if st.button("취소 및 뒤로가기"):
    api.items.cancelReservation(token=st.session_state.token, itemID=st.session_state.item, orderTime=orderNo[:12])
    st.switch_page("pages/5orderPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)