import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

utils.init_session()

# 세션 복구
def try_restore_session():
    # URL 파라미터 확인
    if 'status' not in st.query_params or 'orderNo' not in st.query_params:
        return False

    orderNo : str = st.query_params['orderNo']

    try:
        ref = utils.utilsDb().realtimeDB.reference(f'payment_temp/{orderNo}')
        data = ref.get()
        
        if data:
            st.session_state.token = data.get('token', st.session_state.token)
            st.session_state.payToken = data.get('payToken')
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

# 결제 요청정보 초기화
def orderInfo_clear():
    st.session_state.payToken = None
    st.session_state.item = None
    st.session_state.delicomment = None

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    with st.spinner(text="결제 승인 요청 중...", show_time=False):
        print('결제 승인창 진입')
        if 'status' in st.query_params and st.query_params.get('status') == 'PAY_APPROVED':
            print('파라미터 검증')
            confirmResult : dict = api.pay().confirm_tosspay(
                payToken=st.session_state.payToken,
                orderNo=st.query_params.orderNo
                )
            if confirmResult.get('access'):
                orderTime : str = st.query_params.orderNo[:12]
                order : bool = api.items.itemOrder(
                    token=st.session_state.token,
                    itemID=st.session_state.item,
                    orderTime=orderTime,
                    address=st.session_state.user.get('address')['home'],
                    comment=st.session_state.delicomment,
                    payToken=st.session_state.payToken,
                    pay='toss'
                    )
                if order:
                    st.success(body="주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                    st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                    st.button(label='주문 완료', type='tertiary', on_click=orderInfo_clear, disabled=True)
                    time.sleep(2)
                    st.switch_page("pages/3myPage_orderList.py")
                else:
                    print('주문 중 오류가 발생했습니다. 다시 시도해주세요.')
                    st.warning(body='주문 중 오류가 발생했습니다. 다시 시도해주세요.')
                    time.sleep(2)
                    st.button(label='주문 실패, database 연동 이슈', type='tertiary', on_click=orderInfo_clear, disabled=True)
                    st.rerun()
            else:
                print(f'결제 승인 실패: {confirmResult.get("message")}')
                st.warning(body=f'결제 승인 실패: {confirmResult.get("message")}')
                time.sleep(2)
                st.button(label='주문 실패, 결제 승인 실패', type='tertiary', on_click=orderInfo_clear, disabled=True)
                st.rerun()
        else:
            print('결제 승인 요청이 실패했습니다. 다시 시도해주세요.')
            st.warning(body='결제 승인 요청이 실패했습니다. 다시 시도해주세요.')
            time.sleep(2)
            st.button(label='주문 실패, 결제창 응답 오류', type='tertiary', on_click=orderInfo_clear, disabled=True)
            st.rerun()

else:
    st.switch_page(page='mainPage.py')