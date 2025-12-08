import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
st.html(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

import api
import requests
import time
from datetime import datetime, timezone, timedelta

utils.init_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.item:
    with st.sidebar:
        st.title(body="상품 주문")

    item : str = st.session_state.item
    itemInfo = api.items.showItem().loc[item]

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            type='primary',
            width='content',
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        col1, col2 = st.columns(spec=[2,1], gap="small", vertical_alignment="top")

        with col1:
            st.title(body=itemInfo['name'])
            st.markdown(f"##### ~~{int((itemInfo['price']*100/(100-itemInfo['discount'])//100)*100)}~~")
            st.markdown(body=f"#### :red[{itemInfo['discount']}%] {itemInfo['price']}원")
            st.markdown(body='##### 배송비 :blue[무료배송]')

        col2.image(
            image=str(itemInfo['paths'][0]),
            width='stretch'
            )

        st.markdown(body=f'##### {st.session_state.user.get('address')['home']}')
        st.text_input(
            label='배송 요청사항',
            value=None,
            max_chars=100,
            key='delicomment',
            placeholder='배송 요청사항을 입력해주세요.'
        )

        buyBTN = st.button(
            label='결제하기',
            type='primary',
            width='stretch'
            )

        if buyBTN:
            itemStatus : dict = api.items.itemStatus(itemId=item)
            if itemStatus.get('enable'):
                with st.spinner(text="결제 승인 요청 중...", show_time=False):
                # requests.post()
                    now = datetime.now(timezone.utc) + timedelta(hours=9)
                    orderTime = now.strftime("%y%m%d%H%M%S")

                    order : bool = api.items.itemOrder(token=st.session_state.token, itemID=st.session_state.item, orderTime=orderTime, address=st.session_state.user.get('address')['home'], comment=st.session_state.delicomment)
                    if order:
                        st.success(body=f"{itemInfo['name']} 주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                        st.session_state.item = None # 구매 후 아이템 세션 초기화
                        time.sleep(2)
                        st.switch_page("pages/3myPage_orderList.py")
                    else:
                        st.warning(body='주문 중 오류가 발생했습니다. 다시 시도해주세요.')
                        time.sleep(2)
                        st.session_state.item = None
                        st.rerun()
else:
    st.switch_page(page="mainPage.py")

st.divider()
st.html(body=utils.database().infoAdmin)