import streamlit as st
import time

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = None
if "item" not in st.session_state:
    st.session_state.item = None

# sidebar Nav 기능 비활성화
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.user == None:
    st.error(body="사용자 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
elif st.session_state.item == None:
    st.error(body="상품 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
    st.write(st.session_state.item)