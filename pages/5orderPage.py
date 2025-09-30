import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth
import itemFunc.itemInfo as itemInfo
import requests
import time
from datetime import datetime, timezone, timedelta

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
# 회원 정보 세션
if 'user' not in st.session_state:
    st.session_state.user = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None

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

if any(value is not None for value in st.session_state.token.values()) and st.session_state.item:
    with st.sidebar:
        st.title(body="상품 주문")

    itemIF = itemInfo.items.itemInfo()[st.session_state.item]

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            key='goHOME',
            type='primary',
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        col1, col2 = st.columns(spec=2, gap="small", vertical_alignment="top")

        col1.image(
            image=itemIF.get('paths')[0],
            use_container_width=True
            )

        with col2:
            st.title(body=itemIF.get('name'))
            st.markdown(body=f"##### **가격 :** {itemIF.get('price')}원")
            st.markdown(body="##### **배송비 :** 무료")

        st.markdown(body=f'###### {st.session_state.user.get('address')['home']}')

        buyBTN = st.button(
            label="결제하기",
            key='pay',
            type="primary",
            use_container_width=True
            )

        if buyBTN:
            itemEnable = itemInfo.items.itemStatus(itemId=st.session_state.item)['enable']
            if itemEnable:
                with st.spinner(text="결제 승인 요청 중...", show_time=False):
                # requests.post()
                    now = datetime.now(timezone.utc) + timedelta(hours=9)
                    orderTime = now.strftime("%y%m%d%H%M%S")
                    order = itemInfo.items.itemOrder(
                        token=st.session_state.token,
                        itemID=st.session_state.item,
                        orderTime=orderTime,
                        address=st.session_state.user.get('address')['home']
                        )
                    if order:
                        st.success(body=f"{itemIF.get('name')} 주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                        st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
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