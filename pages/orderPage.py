import streamlit as st
import time
from mainPage import itemsDB

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = False
if "item" not in st.session_state:
    st.session_state.item = False
else:
    st.query_params.item = st.session_state.item

if not st.session_state.user:
    st.error(body="사용자 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
elif not st.session_state.item:
    st.error(body="상품 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
    # 홈으로 이동
    goHome = st.button(
        label="홈으로 이동",
        key="goHome",
        type="primary",
        use_container_width=False,
        disabled=False
    )
    if goHome:
        st.switch_page(page="mainPage.py")
    with st.sidebar:
        st.write(st.session_state.user)
    itemInfo = itemsDB.document(st.session_state.item).get().to_dict()
    st.title(body="구매하기")
    st.write(itemInfo.get("name"))