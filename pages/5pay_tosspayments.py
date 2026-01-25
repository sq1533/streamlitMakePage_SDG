import streamlit as st
import utils
import api
import time
from api.tosspay_handler import handle_payment_callback

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

# 파라미터 및 결제 시도 오류 > 재고 복구
def cancelReservation():
    orderTime = None

    if 'orderId' in st.query_params:
        # orderId 형식: YYYYMMDDHHMMSS_ITEMID_UUID
        # 앞 12자리(YYMMDDHHMMSS) 추출 시도
        try:
            order_id_param = st.query_params['orderId']
            if "_" in order_id_param:
                 orderTime = order_id_param.split('_')[0]
            else:
                 orderTime = order_id_param[:12]
        except:
            pass

    if orderTime:
        # itemID 복구가 필요한 경우 query params에서 파싱 시도할 수 있으나, 
        # 세션 복구 실패 시 st.session_state.item이 없을 수 있음.
        # 여기서는 방어적으로 작성
        item_id = st.session_state.get('item')
        if not item_id and 'orderId' in st.query_params:
             try:
                 parts = st.query_params['orderId'].split('_')
                 if len(parts) >= 2:
                     item_id = parts[1]
             except:
                 pass
        
        if item_id:
            api.items.cancelReservation(token=st.session_state.token, itemID=item_id, orderTime=orderTime)

        if 'toss_order_no' in st.session_state:
            del st.session_state.toss_order_no
        if 'item' in st.session_state:
            del st.session_state.item
        if 'delicomment' in st.session_state:
            del st.session_state.delicomment

# 세션 복구
def try_restore_session():
    # 파라미터 검증
    # Toss Payments V2 Success URL params: paymentKey, orderId, amount
    if 'paymentKey' not in st.query_params:
        cancelReservation()
        return False
    if 'orderId' not in st.query_params:
        cancelReservation()
        return False
    
    orderId : str = st.query_params['orderId']

    try:
        # Realtime DB에서 임시 저장된 데이터 조회 (orderId 키 사용)
        ref = utils.utilsDb().realtimeDB.reference(f"payment_temp/{orderId}")
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            # toss_order_no 저장 (필요 시)
            st.session_state.toss_order_no = orderId 
            st.session_state.item = data.get('item')
            st.session_state.delicomment = data.get('delicomment')
            # 고객정보 재호출
            if st.session_state.token.get('email') or st.session_state.token.get('kakao') or st.session_state.token.get('naver'):
                 st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            
            ref.delete()
            return True
        else:
            print(f"복구할 데이터가 없습니다: {orderId}")
    except Exception as e:
        print(f"DB 오류 (세션 복구): {e}")
    return False

# 세션 복구 실행
restored = try_restore_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    with st.spinner(text="결제 승인 요청 중...", show_time=False):
        
        try:
            toss_secret_key = st.secrets["toss_payments"]["secret_key"]
        except Exception:
            # secrets 설정이 없는 경우 (테스트용)
            toss_secret_key = "TEST_SECRET_KEY" 
            
        # 결제 승인 요청 (handler 모듈 사용)
        payment_result = handle_payment_callback(toss_secret_key)
        
        if payment_result and payment_result["status"] == "success":
            # 승인 성공
            data = payment_result["data"]
            orderId = data.get("orderId")
            
            # orderId 파싱하여 orderTime 추출 (형식: Time_Item_UUID)
            try:
                if "_" in orderId:
                    orderTime = orderId.split('_')[0]
                else:
                    orderTime = orderId[:12]
            except:
                orderTime = datetime.now().strftime("%y%m%d%H%M%S") # Fallback

            # 주문 확정 (DB 저장)
            order : bool = api.items.itemOrder(
                token=st.session_state.token,
                itemID=st.session_state.item,
                orderTime=orderTime,
                address=st.session_state.user.get('address')['home'],
                comment=st.session_state.delicomment,
                payId=data.get("paymentKey"), # 결제 키
                pay='toss_widget' # 결제 수단 구분
                )
                
            if order:
                st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                # 최신 유저 정보 갱신
                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']

                # 세션 정리
                if 'toss_order_no' in st.session_state:
                    del st.session_state.toss_order_no
                if 'item' in st.session_state:
                    del st.session_state.item
                if 'delicomment' in st.session_state:
                    del st.session_state.delicomment

                time.sleep(2)
                st.switch_page("pages/3myPage_orderList.py")
            else:
                print('주문 트랜잭션 실패 -> 자동 환불 진행')
                st.error('상품 재고가 소진되어 주문이 취소되었습니다. 결제가 자동 환불됩니다.')
                
                # 자동 환불 API 호출 (api.pay().refund_tosspay 등 활용 필요)
                # 현재 api.pay에 widget용 취소 로직이 있는지 확인 필요하나, 
                # 5pay_toss.py의 refund_tosspay 재활용 가능성 높음.
                try:
                     api.pay().refund_tosspay(
                        payToken=data.get("paymentKey"), # paymentKey
                        refundNo=orderId, 
                        reason="재고 소진으로 인한 자동 취소"
                    )
                     st.toast("환불이 완료되었습니다.")
                except Exception as e:
                     print(f"자동 환불 실패: {e}")
                     st.toast("환불 처리에 실패했습니다. 고객센터에 문의해주세요.", icon="❌")

                cancelReservation()
                time.sleep(2)
                st.switch_page("pages/5orderPage.py") # 주문 페이지로 복귀

        else:
            # 승인 실패
            msg = payment_result.get("message") if payment_result else "Unknown Error"
            print(f"결제 승인 실패: {msg}")
            st.toast(f"결제 승인 실패: {msg}", icon="❌")
            cancelReservation()
            time.sleep(1)
            st.switch_page("pages/5orderPage.py")
            
else:
    # 세션 복구 실패 또는 비정상 접근
    st.warning("세션이 만료되었거나 비정상적인 접근입니다.")
    time.sleep(1)
    st.switch_page(page='mainPage.py')