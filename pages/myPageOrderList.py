import streamlit as st
import utils
from datetime import datetime

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = False

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = False

st.markdown(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 75% !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
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
            label='HOME',
            key='goHOME',
            type='primary',
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
                status = utils.database().showStatus[order.get('status')]

                # 아이템 정보
                itemInfo = utils.database().pyrebase_db_items.child(itemID).get().val()

                with st.expander(label=f'주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemInfo.get('name')} {status}'):
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
                            'switchPagePath':'pages/userCancel.py',
                            'cancelB':False
                        }
                    elif order.get('status') == 'cancel':
                        btnStatus = {
                            'addressChange':True,
                            'statusChange':'취소 완료',
                            'switchPagePath':'pages/userCancel.py',
                            'cancelB':True
                        }
                    else:
                        btnStatus = {
                            'addressChange':True,
                            'statusChange':'환불 요청',
                            'switchPagePath':'pages/userRefund.py',
                            'cancelB':False
                        }

                    changeAddrB = changeAddr.button(
                        label='배송지 변경',
                        key=f'address_{key}',
                        type='primary',
                        disabled=btnStatus['addressChange'],
                        use_container_width=True
                    )
                    if changeAddrB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page='pages/userCgAddr.py')

                    aboutItem.button(
                        label='상품 상세',
                        key=f'item_{key}',
                        type='primary',
                        use_container_width=True
                    )


                    chagneStatusB = changeStatus.button(
                        label=btnStatus['statusChange'],
                        key=f'order_{key}',
                        type='primary',
                        disabled=btnStatus['cancelB'],
                        use_container_width=True
                    )
                    if chagneStatusB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page=btnStatus['switchPagePath'])