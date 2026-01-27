import streamlit as st
import utils
import api
import time
import streamlit.components.v1 as components
from api.tosspay_handler import handle_payment_callback
from datetime import datetime, timezone

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO - 결제 성공',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)

# iframe 탈출 코드 (결제 성공 시 redirection 문제 해결)


# 페이지 UI 변경 사항
utils.set_page_ui()
utils.init_session()

toss_secret_key = st.secrets["tosspayments"]["secret_key"]

# 세션 복구 function
def try_restore_session():
    orderNo : str = st.query_params.get('orderId')
    
    if not orderNo:
        return None

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
            print(f"복구할 데이터가 없습니다: {orderNo}")
            return None
    except Exception as e:
        print(f"DB 오류 (세션 복구): {e}")
    return None

if 'paymentKey' in st.query_params and 'orderId' in st.query_params:
    sessionData : dict|None = try_restore_session()

    if sessionData:
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
                    st.markdown(
                        f"""
                        <meta http-equiv="refresh" content="0; url=https://amuredo.shop/myPage_orderList">
                        <script>
                            window.top.location.href = "https://amuredo.shop/myPage_orderList";
                        </script>
                        """,
                        unsafe_allow_html=True
                    )
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
            else:
                st.error(f"결제 승인 실패: {payment_result.get('message', '알 수 없는 오류')}")
                time.sleep(2)
                st.switch_page("mainPage.py")
    else:
        st.error("세션 복구에 실패했습니다. 관리자에게 문의하세요.")
        time.sleep(2)
        st.switch_page("mainPage.py")
else:
    st.info("결제 정보가 없습니다.")
    st.switch_page("mainPage.py")