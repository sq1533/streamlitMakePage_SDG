import streamlit as st
import utils
import api
import time
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

try:
    toss_secret_key = st.secrets["toss_payments"]["secret_key"]
    toss_client_key = st.secrets["toss_payments"]["client_key"]
except Exception:
    toss_secret_key = "TEST_SECRET_KEY"
    toss_client_key = "TEST_CLIENT_KEY"

# 세션 복구 function
def try_restore_session():
    if 'paymentKey' not in st.query_params:
        api.items.cancelReservation(token=st.session_state.token, itemID=item, orderTime=orderTime)
        return None
    if 'orderId' not in st.query_params:
        api.items.cancelReservation(token=st.session_state.token, itemID=item, orderTime=orderTime)
        return None
    
    orderNo : str = st.query_params['orderId']

    try:
        # Realtime DB에서 임시 저장된 데이터 조회
        ref = utils.utilsDb().realtimeDB.reference(f"payment_temp/{orderNo}")
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            st.session_state.orderNo = orderNo
            # 고객 정보 호출
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            
            ref.delete()
            return data
        else:
            print(f"복구할 데이터가 없습니다: {orderId}")
            return None
    except Exception as e:
        print(f"DB 오류 (세션 복구): {e}")
    return None

sessionData : dict|None = try_restore_session()

if 'code' in st.query_params and 'message' in st.query_params:
    st.error(f"결제 실패: {st.query_params['message']}")
    time.sleep(1)
    st.switch_page("mainPage.py")

elif 'paymentKey' in st.query_params and 'orderId' in st.query_params and sessionData:
    with st.spinner(text="결제 승인 요청 중...", show_time=False):
        payment_result = handle_payment_callback(toss_secret_key)
            
        if payment_result and payment_result["status"] == "success":
            paymentData = payment_result["data"]
            orderId = paymentData.get("orderId")
            orderTime = orderId[:12]

            # 주문 확정 (DB 저장)
            order : bool = api.items.itemOrder(
                token=st.session_state.token,
                itemID=sessionData.get('item'),
                orderTime=orderTime,
                address=sessionData.get('user_address'),
                comment=sessionData.get('delicomment'),
                payId=data.get("paymentKey"),
                pay='toss_widget'
                )
                    
            if order:
                st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']

                time.sleep(2)
                st.switch_page("pages/3myPage_orderList.py")
            else:
                print('주문 트랜잭션 실패 -> 자동 환불 진행')
                st.error('상품 재고가 소진되어 주문이 취소되었습니다. 결제가 자동 환불됩니다.')
                    
                try:
                    api.pay().refund_tosspay(
                        payToken=data.get("paymentKey"),
                        refundNo=orderId, 
                        reason="재고 소진으로 인한 자동 취소"
                    )
                    st.toast("환불이 완료되었습니다.")
                except Exception as e:
                    print(f"자동 환불 실패: {e}")
                    st.toast("환불 처리에 실패했습니다. 고객센터에 문의해주세요.", icon="❌")
                    api.items.cancelReservation(token=st.session_state.token, itemID=sessionData.get('item'), orderTime=orderTime)
                    time.sleep(2)
                    st.switch_page("mainPage.py")

elif any(value is not None for value in st.session_state.token.values()) and st.session_state.item and st.session_state.orderNo:
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
        success_url="https://amuredo.shop/5pay_tosspayments", 
        fail_url="https://amuredo.shop/5pay_tosspayments",
        height=600
    )
    if st.button("⬅️ 뒤로 가기 (주문 취소)"):
        st.switch_page("pages/5orderPage.py")

else:
    st.error("잘못된 접근입니다.")
    st.switch_page("mainPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)