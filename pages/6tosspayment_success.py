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
            # 고객 정보 호출 (토큰이 유효하다면)
            if 'token' in st.session_state and st.session_state.token.get('accessToken'):
                 st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            
            # 여기서 삭제하지 않고, 주문 성공 후 삭제 (재시도 가능성 고려)
            return data
        else:
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
            amount = int(itemInfo['price'])
            
            paymentKey = st.query_params.get("paymentKey")
            orderId = st.query_params.get("orderId")

            # api.pay 클래스 사용
            payment = api.pay()
            payment_result = payment.confirm_tosspayments(paymentKey, orderId, amount)
                
            if payment_result and payment_result["status"] == "success":
                paymentData = payment_result["data"]
                # 주문 시간은 orderNo Prefix (12자리)
                orderTime = orderId[:12]

                # 주문 확정 (DB 저장)
                order : bool = api.items.itemOrder(
                    token=st.session_state.token,
                    itemID=sessionData.get('item'),
                    orderTime=orderTime,
                    address=sessionData.get('user_address'),
                    comment=sessionData.get('delicomment'),
                    payId=paymentKey,
                    pay='toss_widget'
                )
                        
                if order:
                    st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                    # 임시 데이터 삭제
                    try:
                        utils.utilsDb().realtimeDB.reference(f"payment_temp/{orderId}").delete()
                    except:
                        pass

                    time.sleep(2)
                    st.switch_page("pages/3myPage_orderList.py")
                else:
                    print('주문 트랜잭션 실패 -> 자동 환불 진행')
                    st.error('상품 재고가 소진되어 주문이 취소되었습니다. 결제가 자동 환불됩니다.')
                        
                    # 환불
                    payment.refund_tosspayments(paymentKey=paymentKey, cancelReason="재고 소진으로 인한 자동 취소")
                    st.toast("환불이 완료되었습니다.")
                    
                    api.items.cancelReservation(token=st.session_state.token, itemID=sessionData.get('item'), orderTime=orderTime)
                    time.sleep(2)
                    st.switch_page("mainPage.py")
            else:
                st.error(f"결제 승인 실패: {payment_result.get('message', '알 수 없는 오류')}")
                api.items.cancelReservation(token=st.session_state.token, itemID=sessionData.get('item'), orderTime=orderId[:12])
                time.sleep(2)
                st.switch_page("mainPage.py")
    else:
        st.error("세션(주문정보) 복구에 실패했습니다. 관리자에게 문의하세요.")
        time.sleep(2)
        st.switch_page("mainPage.py")
else:
    st.info("결제 정보가 없습니다.")
    st.switch_page("mainPage.py")
