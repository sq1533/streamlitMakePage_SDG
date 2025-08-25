import streamlit as st
import utils
from datetime import datetime, timezone, timedelta
import time
import requests

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = False

st.markdown(
    body="""
    <style>
    button[data-testid="stBaseButton-elementToolbar"][aria-label="Fullscreen"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 80% !important;
        max-width: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not st.session_state.user:
    st.switch_page(page="mainPage.py")
else:

    userInfo = utils.database().pyrebase_db_user.child(st.session_state.user['localId']).get(st.session_state.user['idToken']).val()

    with st.sidebar:
        st.title(body="주문내역")

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
        
        st.markdown(body="주문 내역")
        if userInfo.get('orderList') == None:
            st.markdown(body="아직 주문내역이 없습니다.")
        else:
            for key, order in reversed(userInfo.get('orderList').items()):
                # 주문 정보
                orderTime = order.get('time')
                itemID = order.get('item')
                address = order.get('address')
                status = order.get('status')

                # 아이템 정보
                itemInfo = utils.database().pyrebase_db_items.child(itemID).get().val()

                with st.expander(label=f'주문 시간 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemInfo.get('name')} {status}'):
                    image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                    image.image(
                        image=itemInfo.get("paths")[0],
                        caption=None,
                        use_container_width=True,
                        clamp=False,
                        output_format="auto"
                        )
                    info.markdown(
                        body=f"""
                        상품명 : {itemInfo.get('name')}\n\n
                        {address}
                        """
                        )