import streamlit as st
import time
import requests
from utils import userInfoDB, now, datetime

# 쿼리, 세션 관리
if "user" not in st.session_state:
    st.session_state.user = False

# check cancel
@st.dialog(title="취소하시겠습니까?")
def checkCancel(cancelItem):
    NO, YES = st.columns(spec=[1,1], gap="small", vertical_alignment="center")
    NOBTN = NO.button(
        label="아니요.",
        key=f"noCancel_{cancelItem}",
        type="secondary",
        use_container_width=True
    )
    YESBTN = YES.button(
        label="네, 취소하겠습니다.",
        key=f"yesCancel_{cancelItem}",
        type="primary",
        use_container_width=True
    )
    if NOBTN:
        st.rerun()
    if YESBTN:
        cancelOrder(cancelItem)
# 2025-06-08 21:22 / EE250603003
# cancel order 결제 취소 API 추가
def cancelOrder(cancelItem):
    if not st.session_state.user:
        pass
    else:
        user_doc = userInfoDB.document(st.session_state.user["id"]).get()
        if cancelItem in st.session_state.user.get("orders"):
            # requests.post()
            st.session_state.user["orders"].append(cancelItem + "_" + "cancel")
            st.session_state.user["orders"].remove(cancelItem)
            user_doc.reference.update({"orders": st.session_state.user["orders"]})
            st.rerun()
        else:
            st.error("주문 취소 실패, 고객센터에 문의해주세요.")

if not st.session_state.user:
    st.error(body="사용자 정보가 없습니다. 메인페이지 이동중")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
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
        if not st.session_state.user.get("orders"):
            st.markdown(body="아직 주문내역이 없습니다.")
        else:
            for order in reversed(st.session_state.user.get("orders")):
                orderDay = order.split(" ")[0]
                nowDay = now.strftime("%Y-%m-%d")
                orderDay_d = datetime.strptime(orderDay, "%Y-%m-%d").date()
                nowDay_d = datetime.strptime(nowDay, "%Y-%m-%d").date()
                elapsed = (nowDay_d - orderDay_d).days
                orderThings, cancel = st.columns(spec=[4,1], gap="small", vertical_alignment="center")
                orderThings.markdown(body=order)
                if "_cancel" in order:
                    disabled = True
                elif elapsed > 20:
                    disabled = True
                else:
                    disabled = False
                cancelBTN = cancel.button(
                    label="취소",
                    key=f"cancel_{order}",
                    type="secondary",
                    use_container_width=True,
                    disabled=disabled
                )
                if cancelBTN:
                    checkCancel(order)