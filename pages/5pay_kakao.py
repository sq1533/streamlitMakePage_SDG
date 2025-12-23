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
utils.set_page_ui()
utils.init_session()

# 파라미터 및 결제 시도 오류 > 재고 복구 (기존 로직 재사용)
def cancelReservation():
    orderTime = None
    if 'orderNo' in st.query_params:
        orderTime = st.query_params['orderNo'][:12]

    if orderTime:
        api.items.cancelReservation(token=st.session_state.token, itemID=st.session_state.item, orderTime=orderTime)

        if 'tid' in st.session_state:
            del st.session_state.tid
        if 'item' in st.session_state:
            del st.session_state.item
        if 'delicomment' in st.session_state:
            del st.session_state.delicomment

# 세션 복구
def try_restore_session():
    # URL 파라미터 확인
    if 'pg_token' not in st.query_params or 'orderNo' not in st.query_params:
        cancelReservation()
        return False

    orderNo : str = st.query_params['orderNo']

    try:
        ref = utils.utilsDb().realtimeDB.reference(f'payment_temp/{orderNo}')
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            st.session_state.tid = data.get('tid')
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

# 메인 로직
if any(value is not None for value in st.session_state.token.values()):
    pg_token = st.query_params['pg_token']
    orderNo = st.query_params['orderNo']

    if 'tid' not in st.session_state:
        st.error("결제 세션이 만료되었습니다. 다시 시도해주세요.")
    else:
        with st.spinner("결제 승인 중..."):
            approve_result = api.pay().approve_kakaopay(
                tid=st.session_state.tid,
                pg_token=pg_token,
                orderNo=orderNo
            )
            if approve_result['access']:

                orderTime = orderNo[:12]

                order_success = api.items.itemOrder(
                    token=st.session_state.token,
                    itemID=st.session_state.item,
                    orderTime=orderTime,
                    address=st.session_state.user.get('address')['home'],
                    comment=st.session_state.delicomment,
                    payId=st.session_state.tid,
                    pay='kakao'
                )

                if order_success:
                    st.success("주문이 완료되었습니다.")
                    st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']

                    if 'tid' in st.session_state:
                        del st.session_state.tid
                    if 'item' in st.session_state:
                        del st.session_state.item
                    if 'delicomment' in st.session_state:
                        del st.session_state.delicomment

                    time.sleep(2)
                    st.switch_page("pages/3myPage_orderList.py")
                else:
                    st.error("재고 소진 등의 이유로 주문 처리에 실패했습니다. (자동 환불 필요)")
                    # 환불 로직 추가 필요 (Cancel API) - 현재 구현 범위 밖
                    cancelReservation()
            else:
                st.error(f"결제 승인 실패: {approve_result.get('message')}")
                cancelReservation()
else:
    st.switch_page('mainPage.py')
