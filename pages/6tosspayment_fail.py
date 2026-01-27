import streamlit as st
import utils
import api
import time

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

code = st.query_params.get("code")
message = st.query_params.get("message")
orderId = st.query_params.get("orderId")

st.error("결제에 실패했습니다.")
if message:
    st.write(f"사유: {message} ({code})")

st.divider()

if st.button("돌아가기 (주문 재시도)"):
    # 예약 취소 등 후처리
    if orderId and 'token' in st.session_state and st.session_state.token.get('accessToken'):
         api.items.cancelReservation(token=st.session_state.token, itemID=st.session_state.item, orderTime=orderId[:12])
    st.switch_page("pages/5orderPage.py")

# 자동 이동
time.sleep(5)
st.switch_page("pages/5orderPage.py")
