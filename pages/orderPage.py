import streamlit as st
import time
from mainPage import itemsDB

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = None
if "item" not in st.session_state:
    st.session_state.item = None

if st.session_state.user == None:
    st.error(body="사용자 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
elif st.session_state.item == None:
    st.error(body="상품 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
    with st.sidebar:
        st.write(st.session_state.user)
    itemInfo = itemsDB.document(st.session_state.item).get().to_dict()
    st.title(body=itemInfo.get("name"))