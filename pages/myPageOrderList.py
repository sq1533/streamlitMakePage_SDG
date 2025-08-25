import streamlit as st
import utils
from datetime import datetime

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
            showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료'
            }
            for key, order in reversed(userInfo.get('orderList').items()):
                # 주문 정보
                orderTime = order.get('time')
                itemID = order.get('item')
                address = order.get('address')
                status = showStatus[order.get('status')]

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
                    
                    changeAddr, aboutItem, changeStatus = st.columns(spec=3, gap="small", vertical_alignment="center")

                    if order.get('status') == 'ready':
                        btnStatus = {
                            'addressChange':False,
                            'statusChange':'주문 취소',
                            'switchPagePath':'pages/userCancel.py'
                        }
                    else:
                        btnStatus = {
                            'addressChange':True,
                            'statusChange':'환불 요청',
                            'switchPagePath':'pages/userRefund.py'
                        }

                    changeAddrB = changeAddr.button(
                        label='배송지 변경',
                        key=f'address_{key}',
                        type='primary',
                        disabled=btnStatus['addressChange'],
                        use_container_width=True
                    )
                    if changeAddrB:
                        resultAddr = st.radio(
                            label="상품 배송지",
                            options=userInfo.get('address').values(),
                            index=0,
                            key=f'changeAddr_{key}',
                            horizontal=False,
                            label_visibility="visible"
                            )

                    aboutItem.button(
                        label='상품 상세',
                        key=f'item_{key}',
                        type='primary',
                        use_container_width=True
                    )


                    changeStatus.button(
                        label=btnStatus['statusChange'],
                        key=f'order_{key}',
                        type='primary',
                        use_container_width=True
                    )