import streamlit as st
import time
import requests
from utils import userInfoDB, itemsDB

# 세션 관리
if "user" not in st.session_state:
    st.session_state.user = False

user_doc = userInfoDB.document(st.session_state.user["id"]).get()

# check cancel
@st.dialog(title="진행 하시겠습니까?")
def checkCancel(cancelItem):
    if "_delivery" in cancelItem:
        st.info(body="이미 발송된 상품입니다. 발송된 주소로 회수되며, 택배비를 제외한 가격으로 반품됩니다.")
        NO, YES = st.columns(spec=[1,1], gap="small", vertical_alignment="center")
        NOBTN = NO.button(
            label="아니요.",
            key=f"noCancel_{cancelItem}",
            type="secondary",
            use_container_width=True
        )
        YESBTN = YES.button(
            label="네, 반품 하겠습니다.",
            key=f"yesCancel_{cancelItem}",
            type="primary",
            use_container_width=True
        )
        if NOBTN:
            st.rerun()
        if YESBTN:
            # 반품 리스트 추가
            st.rerun()
    elif "_complete" in cancelItem:
        st.info(body="반품은 상품 발송된 주소로 회수되며, 택배비를 제외한 가격으로 반품됩니다.")
        NO, YES = st.columns(spec=[1,1], gap="small", vertical_alignment="center")
        NOBTN = NO.button(
            label="아니요.",
            key=f"noCancel_{cancelItem}",
            type="secondary",
            use_container_width=True
        )
        YESBTN = YES.button(
            label="네, 반품 하겠습니다.",
            key=f"yesCancel_{cancelItem}",
            type="primary",
            use_container_width=True
        )
        if NOBTN:
            st.rerun()
        if YESBTN:
            # 반품 리스트 추가
            st.rerun()
    else:
        NO, YES = st.columns(spec=[1,1], gap="small", vertical_alignment="center")
        NOBTN = NO.button(
            label="아니요.",
            key=f"noCancel_{cancelItem}",
            type="secondary",
            use_container_width=True
        )
        YESBTN = YES.button(
            label="네, 취소 하겠습니다.",
            key=f"yesCancel_{cancelItem}",
            type="primary",
            use_container_width=True
        )
        if NOBTN:
            st.rerun()
        if YESBTN:
            cancelOrder(cancelItem)

# cancel order 결제 취소 API 추가
def cancelOrder(cancelItem):
    if not st.session_state.user:
        pass
    else:
        if cancelItem in st.session_state.user.get("orders"):
            # requests.post()
            st.session_state.user["orders"].append(cancelItem + "_" + "cancel")
            st.session_state.user["orders"].remove(cancelItem)
            st.session_state.user["orders"].sort()
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
                itemID = order.split("/")[1].split("_")[0]
                orderTime = order.split("/")[0]
                itemInfo = itemsDB.document(itemID).get().to_dict()
                orderImage, orderInfo, cancel = st.columns(spec=[1,4,1], gap="small", vertical_alignment="center")
                orderImage.image(
                    image=itemInfo.get("path"),
                    caption=None,
                    use_container_width=True,
                    clamp=False,
                    output_format="auto"
                    )
                orderInfo.markdown(body=f"상품명 : {itemInfo.get("name")} // 주문 날짜 : {orderTime}")
                if "_cancel" in order:
                    cancel.button(
                        label="취소 완료",
                        key=f"cancel_{order}_complete",
                        type="secondary",
                        use_container_width=True,
                        disabled=True
                    )
                elif "_delivery" in order:
                    cancelBTN = cancel.button(
                        label="취소 요청하기",
                        key=f"cancel_{order}_request",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)
                elif "_complete" in order:
                    cancelBTN = cancel.button(
                        label="반품 신청하기",
                        key=f"return_{order}",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)
                else:
                    cancelBTN = cancel.button(
                        label="취소",
                        key=f"cancel_{order}",
                        type="secondary",
                        use_container_width=True,
                        disabled=False
                    )
                    if cancelBTN:
                        checkCancel(order)