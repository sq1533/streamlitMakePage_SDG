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

# 파라미터 및 결제 시도 오류 > 재고 복구
def cancelReservation():
    orderTime = None

    if 'orderNo' in st.query_params:
        orderTime = st.query_params['orderNo'][:12]

    if orderTime:
        api.items.cancelReservation(token=st.session_state.token, itemID=st.session_state.item, orderTime=orderTime)

        if 'reserveId' in st.session_state:
            del st.session_state.reserveId
        if 'item' in st.session_state:
            del st.session_state.item
        if 'delicomment' in st.session_state:
            del st.session_state.delicomment

# 세션 복구
def try_restore_session():
    # 파라미터 검증
    if 'resultCode' not in st.query_params:
        cancelReservation()
        return False
    if 'paymentId' not in st.query_params:
        cancelReservation()
        return False
    if st.query_params.resultCode != 'Success':
        cancelReservation()
        return False
    if 'orderNo' not in st.query_params:
        cancelReservation()
        return False

    orderNo : str = st.query_params['orderNo']

    try:
        ref = utils.utilsDb().realtimeDB.reference(f'payment_temp/{orderNo}')
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            st.session_state.reserveId = data.get('reserveId') # reserveId 저장
            st.session_state.item = data.get('item')
            st.session_state.delicomment = data.get('delicomment')
            # 고객정보 재호출
            st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
            
            ref.delete()
            return True
        else:
            print("복구할 데이터가 없습니다.")
    except Exception as e:
        print(f"DB 오류: {e}")
    return False

try_restore_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    with st.spinner(text="결제 승인 요청 중...", show_time=False):
        # 네이버페이 리다이렉트 파라미터 확인
        paymentId : str = st.query_params['paymentId']
            
        confirmResult : dict = api.pay().approve_naverpay(paymentId=paymentId)
            
        if confirmResult.get('access'):
            # orderNo는 쿼리 파라미터에서 가져옴
            orderNo = st.query_params.get('orderNo')
            orderTime = orderNo[:12]
                
            # 주문 확정
            order : bool = api.items.itemOrder(
                token=st.session_state.token,
                itemID=st.session_state.item,
                orderTime=orderTime,
                address=st.session_state.user.get('address')['home'],
                comment=st.session_state.delicomment,
                payId=paymentId, # 네이버페이 결제 번호
                pay='naver'
                )
                
            if order:
                st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']

                if 'reserveId' in st.session_state:
                    del st.session_state.reserveId
                if 'item' in st.session_state:
                    del st.session_state.item
                if 'delicomment' in st.session_state:
                    del st.session_state.delicomment

                time.sleep(2)
                st.switch_page("pages/3myPage_orderList.py")
            else:
                print('주문 트랜잭션 실패 -> 자동 취소 필요')
                st.error('상품 재고가 소진되어 주문이 취소되었습니다. (결제 취소 필요)')
                cancelReservation()
                st.rerun()

        else:
            print(f'결제 승인 실패: {confirmResult.get("message")}')
            st.toast(f'결제 승인 실패: {confirmResult.get("message")}', icon="❌")
            cancelReservation()
            time.sleep(0.7)
            st.rerun()
else:
    st.switch_page(page='mainPage.py')