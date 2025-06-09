import streamlit as st
import time
import requests
from utils import itemsDB, userInfoDB, now

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = False
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
# 사용자 로그아웃
def logout():
    st.session_state.user = False
    st.rerun()

if not st.session_state.user:
    st.error(body="사용자 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
elif not st.session_state.item:
    st.error(body="상품 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:

    with st.sidebar:
        st.title(body="상품 주문")

    itemInfo = itemsDB.document(st.session_state.item).get().to_dict()

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
                image=itemInfo.get("path"),
                use_container_width=True
                )

        with col2:
            st.title(body=itemInfo.get("name"))
            st.markdown(
                body=f"##### **가격 :** {itemInfo.get('price')}원"
                )
            st.markdown(
                body=f"##### **배송비 :** 무료"
                )

        addressTarget = st.radio(
            label="상품 배송지",
            options=st.session_state.user["address"],
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
            st.success(f"{itemInfo.get('name')} 구매가 완료되었습니다! (실제 결제 기능은 구현되지 않았습니다.)")
            with st.spinner(text="결제 승인 요청 중...", show_time=False):
                # requests.post()
                orderTime = now.strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.user["orders"].append(orderTime + " / " + st.session_state.item)
                user_doc = userInfoDB.document(st.session_state.user["id"]).get()
                user_doc.reference.update({"orders":st.session_state.user["orders"]})
                st.session_state.item = False # 구매 후 아이템 세션 초기화
                st.switch_page("pages/myPageOrderList.py")