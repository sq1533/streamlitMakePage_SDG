import streamlit as st
import utils
import requests
import time
from datetime import datetime, timezone, timedelta

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = False

# 회원 허용 유무
if "userAllow" not in st.session_state:
    st.session_state.userAllow = False

# 상품 구매 페이지
if "item" not in st.session_state:
    st.session_state.item = False

st.markdown(
    """
    <style>
    button[data-testid="stBaseButton-elementToolbar"][aria-label="Fullscreen"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.userAllow:
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
                label="홈으로 이동",
                key="goHomeFromOrderPage",
                type="primary",
                use_container_width=False,
                disabled=False
            )
            if goHome:
                st.switch_page(page="mainPage.py")

            col1, col2 = st.columns(spec=2, gap="small", vertical_alignment="top")

            with col1:
                st.image(
                    image=itemInfo['paths'][0],
                    use_container_width=True
                    )

            with col2:
                st.title(body=itemInfo['name'])
                st.markdown(
                    body=f"##### **가격 :** {itemInfo['price']}원"
                    )
                st.markdown(
                    body="##### **배송비 :** 무료"
                    )

            address = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).get(token=st.session_state.user['idToken']).val()['address']['home']
            addressTarget = st.radio(
                label="상품 배송지",
                options=address,
                index=0,
                key="targetAdd",
                horizontal=False,
                label_visibility="visible"
                )
            buyBTN = st.button(
                label="결제하기",
                type="primary",
                use_container_width=True
                )
            if buyBTN:
                with st.spinner(text="결제 승인 요청 중...", show_time=False):
                    # requests.post()
                    now = datetime.now(timezone.utc) + timedelta(hours=9)
                    orderTime = now.strftime("%y%m%d%H%M%S")
                    orderInfo = {
                        'user' : st.session_state.user['localId'],
                        'time' : orderTime,
                        'item' : st.session_state.item,
                        'address' : addressTarget,
                        'status' : 'ready'
                        }
                    order = utils.items.itemOrder(
                        uid=st.session_state.user['localId'],
                        token=st.session_state.user['idToken'],
                        itemID=st.session_state.item,
                        orderInfo=orderInfo
                        )
                    if order:
                        st.success(
                            body=f"{itemInfo['name']} 주문 진행 중입니다."
                            )
                        st.session_state.item = False # 구매 후 아이템 세션 초기화
                        time.sleep(3)
                        st.switch_page("mainPage.py") # 구매 완료 후 주문완료 페이지 전환
                    else:
                        st.warning(
                            body='주문 중 오류가 발생했습니다. 다시 시도해주세요.'
                        )
                        time.sleep(3)
                        st.session_state.item = False # 구매 후 아이템 세션 초기화
                        st.rerun()
else:
    st.switch_page(page="mainPage.py")