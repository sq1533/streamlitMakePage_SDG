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

# iframe 탈출 코드 (결제 성공 시 redirection 문제 해결)
# Toss Payments 위젯이 iframe 내에서 리다이렉트 될 때, 상위 창(window.top)을 리다이렉트 URL로 이동시킵니다.
components.html(
    """
    <script>
        try {
            // 현재 창(window.self)이 최상위 창(window.top)과 다르고 (iframe 내부)
            // URL에 paymentKey 등의 파라미터가 포함되어 있다면 (결제 리다이렉트 후)
            if (window.self !== window.top && window.location.search.includes("paymentKey")) {
                // 부모 창(window.top)을 현재 URL(파라미터 포함)로 이동시킵니다.
                window.top.location.href = window.location.href;
            }
        } catch (e) {
            console.error("Frame breakout failed", e);
        }
    </script>
    """,
    height=0
)

# 페이지 UI 변경 사항
utils.set_page_ui()

utils.init_session()

if 'orderNo' not in st.session_state:
    st.session_state.orderNo = None

toss_secret_key = st.secrets["tosspayments"]["secret_key"]
toss_client_key = st.secrets["tosspayments"]["client_key"]

# 세션 복구 function
def try_restore_session():
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

if 'code' in st.query_params and 'message' in st.query_params:
    st.error(f"결제 실패: {st.query_params['message']}")
    time.sleep(1)
    st.switch_page("mainPage.py")

elif 'paymentKey' in st.query_params and 'orderId' in st.query_params:
    sessionData : dict|None = try_restore_session()

    with st.spinner(text="결제 승인 요청 중...", show_time=False):
        # 금액 검증을 위한 실제 아이템 가격 조회
        itemInfo = api.items.showItem().loc[sessionData.get('item')]

        payment_result = handle_payment_callback(toss_secret_key, expected_amount=int(itemInfo['price']))
            
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
                payId=st.query_params.paymentKey,
                pay='toss_widget'
                )
                    
            if order:
                st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                try:
                    utils.utilsDb().realtimeDB.reference(f"payment_temp/{st.query_params['orderId']}").delete()
                except:
                    pass

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
        success_url="https://amuredo.shop/pay_tosspayments",
        fail_url="https://amuredo.shop/pay_tosspayments",
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