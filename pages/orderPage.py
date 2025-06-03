import streamlit as st
import time
from utils import itemsDB

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = False
if "item" not in st.session_state:
    st.session_state.item = False

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

    with st.sidebar:
        st.title(body="상품 주문")

    itemInfo = itemsDB.document(st.session_state.item).get().to_dict()
    st.title(body=itemInfo.get("name"))
    item_id_to_buy = st.session_state.item
    item_doc_ref = itemsDB.document(item_id_to_buy)
    item_doc = item_doc_ref.get()
    if item_doc.exists:
        item_data = item_doc.to_dict()
        col1, col2 = st.columns([1,2])
        with col1:
            st.image(item_data.get("path"), use_container_width=True)
        with col2:
            st.markdown(f"**가격:** {item_data.get('price')}원")
            
            if st.button("결제하기", type="primary", use_container_width=True):
                st.success(f"{item_data.get('name')} 구매가 완료되었습니다! (실제 결제 기능은 구현되지 않았습니다.)")
                # st.session_state.item = False # 구매 후 아이템 세션 초기화
                # time.sleep(3)
                # st.switch_page("mainPage.py")
    else:
        st.error("선택하신 상품 정보를 찾을 수 없습니다. 메인 페이지로 돌아갑니다.")
        time.sleep(2)
        st.switch_page("mainPage.py")