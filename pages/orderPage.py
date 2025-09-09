import streamlit as st
import utils
import requests
import time
from datetime import datetime, timezone, timedelta

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False
# 회원 정보
if "userInfo" not in st.session_state:
    st.session_state.userInfo = None

# 상품 구매 페이지
if "item" not in st.session_state:
    st.session_state.item = False

st.markdown(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.userInfo.get('emailCK'):
    if not st.session_state.item:
        st.switch_page(page="mainPage.py")
    else:
        with st.sidebar:
            st.title(body="상품 주문")

        itemInfo = utils.database().pyrebase_db_items.child(st.session_state.item).get().val()
        itemStatus = utils.database().pyrebase_db_itemStatus.child(st.session_state.item).get().val()

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
                st.session_state.item = False
                st.switch_page(page="mainPage.py")

            col1, col2 = st.columns(spec=2, gap="small", vertical_alignment="top")

            col1.image(
                image=itemInfo['paths'][0],
                use_container_width=True
                )

            with col2:
                st.title(body=itemInfo['name'])
                st.markdown(body=f"##### **가격 :** {itemInfo['price']}원")
                st.markdown(body="##### **배송비 :** 무료")

            st.markdown(body=f'###### {st.session_state.userInfo.get('address')['home']}')

            buyBTN = st.button(
                label="결제하기",
                key='pay',
                type="primary",
                use_container_width=True
                )

            if buyBTN:
                with st.spinner(text="결제 승인 요청 중...", show_time=False):
                    # requests.post()
                    now = datetime.now(timezone.utc) + timedelta(hours=9)
                    orderTime = now.strftime("%y%m%d%H%M%S")
                    order = utils.items.itemOrder(
                        uid=st.session_state.user['localId'],
                        token=st.session_state.user['idToken'],
                        itemID=st.session_state.item,
                        orderTime=orderTime,
                        address=st.session_state.userInfo.get('address')['home']
                        )
                    if order:
                        st.success(body=f"{itemInfo['name']} 주문이 완료 되었습니다. 주문 내역으로 이동합니다.")
                        st.session_state.userInfo = utils.guest.showUserInfo(uid=st.session_state.user['localId'], token=st.session_state.user['token'])
                        st.session_state.item = False # 구매 후 아이템 세션 초기화
                        time.sleep(2)
                        st.switch_page("pages/myPageOrderList.py")
                    else:
                        st.warning(body='주문 중 오류가 발생했습니다. 다시 시도해주세요.')
                        time.sleep(2)
                        st.session_state.item = False # 구매 후 아이템 세션 초기화
                        st.rerun()
else:
    st.switch_page(page="mainPage.py")