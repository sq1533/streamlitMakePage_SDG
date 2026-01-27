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
    # Toss Widget에서 넘어온 suffixed orderId (예: order123_1789...)
    widget_orderId : str = st.query_params.get('orderId')
    
    if not widget_orderId:
        return None, None

    # 실제 DB 조회용 orderNo (Suffix 제거)
    real_orderNo = widget_orderId.split('_')[0] if '_' in widget_orderId else widget_orderId

    try:
        # Realtime DB에서 임시 저장된 데이터 조회 (real_orderNo 사용)
        ref = utils.utilsDb().realtimeDB.reference(f"payment_temp/{real_orderNo}")
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            st.session_state.orderNo = real_orderNo
            # 고객 정보 호출 (토큰이 유효하다면)
            if 'token' in st.session_state and st.session_state.token.get('accessToken'):
                 st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            
            # 여기서 삭제하지 않고, 주문 성공 후 삭제
            return data, real_orderNo
        else:
            return None, real_orderNo
    except Exception as e:
        print(f"DB 오류 (세션 복구): {e}")
    return None, real_orderNo

if 'paymentKey' in st.query_params and 'orderId' in st.query_params:
    sessionData, real_orderNo = try_restore_session()

    if sessionData:
        with st.spinner(text="결제 승인 요청 중...", show_time=False):
            # 금액 검증을 위한 실제 아이템 가격 조회
            itemInfo = api.items.showItem().loc[sessionData.get('item')]
            amount = int(itemInfo['price'])
            
            paymentKey = st.query_params.get("paymentKey")
            widget_orderId = st.query_params.get("orderId")

            # api.pay 클래스 사용
            # 중요: Toss 서버에는 요청했던 widget_orderId(suffix 포함)를 그대로 보내야 함
            payment = api.pay()
            payment_result = payment.confirm_tosspayments(paymentKey, widget_orderId, amount)
                
            if payment_result and payment_result["status"] == "success":
                paymentData = payment_result["data"]
                # 주문 시간은 실제 orderNo 기준 (prefix 12자리)
                orderTime = real_orderNo[:12]

                # 주문 확정 (DB 저장) - 여기서는 real_orderNo 관련 정보 사용
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
                    # 임시 데이터 삭제 (real_orderNo 사용)
                    try:
                        utils.utilsDb().realtimeDB.reference(f"payment_temp/{real_orderNo}").delete()
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
                    
                    api.items.cancelReservation(token=st.session_state.token, itemID=sessionData.get('item'), orderTime=real_orderNo[:12])
                    time.sleep(2)
                    st.switch_page("mainPage.py")
            else:
                st.error(f"결제 승인 실패: {payment_result.get('message', '알 수 없는 오류')}")
                api.items.cancelReservation(token=st.session_state.token, itemID=sessionData.get('item'), orderTime=real_orderNo[:12])
                time.sleep(2)
                st.switch_page("mainPage.py")
    else:
        st.error("세션(주문정보) 복구에 실패했습니다. 관리자에게 문의하세요.")
        time.sleep(2)
        st.switch_page("mainPage.py")
else:
    st.info("결제 정보가 없습니다.")
    st.switch_page("mainPage.py")
