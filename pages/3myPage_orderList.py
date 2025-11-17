import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=':a:',
    layout='wide',
    initial_sidebar_state='auto'
)
st.html(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

import api
import utils
import time
from datetime import datetime

# 회원 토큰 세션 및 정보
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None
# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = None

def imgLoad(path : str):
    if path:
        return st.image(
            image=path,
            output_format='JPEG'
        )
    else:
        return st.info(body='not image')

# 회원 로그인 확인
if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title(body="주문내역")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            type='primary',
            width='content',
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")
        
        st.markdown(body="주문 내역")

        userOrder : dict = st.session_state.user.get('orderList')

        if userOrder:
            # 아이템 정보 호출
            itemList : dict = api.items.showItem()

            for key, order in reversed(st.session_state.user.get('orderList').items()):
                # 주문 정보
                orderTime = key
                itemID = order.get('item')
                address = order.get('address')
                feedback = order.get('feedback')
                status = utils.database().showStatus[order.get('status')]

                # 상품
                itemIF = itemList.get(itemID)

                with st.expander(label=f'주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemIF.name} {status}'):
                    # 상품 이미지, 정보 호출
                    image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                    with image.container():
                        imgLoad(str(itemIF.paths[0]))
                    info.markdown(body=f'상품명 : {itemIF.name}\n\n{address}')

                    # 후기 유무 검사
                    if feedback:
                        fbDisable = True
                    else:
                        fbDisable = False
                    # 후기 입력
                    feedT, feed, feedB = info.columns(spec=[2,1,1], gap='small', vertical_alignment='center')
                    fdt = feedT.text_input(
                        label='후기 남기기',
                        value=None,
                        max_chars=20,
                        key=f'feedText_{key}',
                        placeholder='상품은 어떠셨나요?',
                        disabled=fbDisable,
                        label_visibility='collapsed'
                    )
                    fbing = feed.feedback(
                        options='thumbs',
                        key=f'itemFB_{key}',
                        disabled=fbDisable
                        )
                    fbB = feedB.button(
                        label='평가하기',
                        key=f'feedbackAdd_{key}',
                        type='secondary',
                        disabled=fbDisable,
                        width='stretch'
                    )
                    if fbB:
                        if fbing:
                            feadbackDone = api.items.addFeedback(token=st.session_state.token, key=orderTime, itemID=itemID, feedback=fbing, feedT=fdt)
                            if feadbackDone:
                                st.info(body='소중한 의견 감사합니다.')
                                time.sleep(2)
                                st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)
                                st.rerun()
                            else:
                                st.warning(body='평가 중 오류발생')
                        else:
                            st.info(body='평가 미입력, 재확인 바랍니다.')

                    # 주문 상태 확인 및 설정 변경
                    changeAddr, aboutItem, changeStatus = st.columns(spec=3, gap="small", vertical_alignment="center")

                    if order.get('status') == 'ready': # 상품 준비중 > 배송지 변경 가능, 주문 취소 가능
                        btnStatus = {
                            'addressChange' : False,
                            'cancelB' : False,
                            'statusChange' : '주문 취소',
                            'switchPagePath' : 'pages/4myOrder_itemCancel.py'
                        }
                    elif order.get('status') == 'Done': # 배송 완료 후 7일 경과 > 배송지 변경, 환불 불가
                        btnStatus = {
                            'addressChange' : True,
                            'cancelB' : True,
                            'statusChange' : '완료',
                            'switchPagePath' : 'mainPage.py'
                        }
                    elif order.get('status') == 'cancel': # 주문 취소 > 배송지 변경 불가, 주문 상태 변경 불가
                        btnStatus = {
                            'addressChange' : True,
                            'cancelB' : True,
                            'statusChange' : '취소 완료',
                            'switchPagePath' : 'mainPage.py'
                        }
                    elif order.get('status') == 'refund': # 상품 환불 요청 > 배송지 변경 불가, 주문 상태 변경 불가
                        btnStatus = {
                            'addressChange' : True,
                            'cancelB' : True,
                            'statusChange' : '환불 진행 중..',
                            'switchPagePath' : 'mainPage.py'
                        }
                    elif order.get('status') == 'refunded': # 상품 환불 완료 > 배송지 변경 불가, 주문 상태 변경 불가
                        btnStatus = {
                            'addressChange' : True,
                            'cancelB' : True,
                            'statusChange' : '환불 완료',
                            'switchPagePath' : 'mainPage.py'
                        }
                    else: # 상품 배송중 or 상품 배송완료( 7일 경과 전 )
                        btnStatus = {
                            'addressChange' : True,
                            'cancelB' : False,
                            'statusChange' : '환불 요청',
                            'switchPagePath' : 'pages/4myOrder_itemRefund.py'
                        }

                    # 주문 상품 배송지 변경
                    changeAddrB = changeAddr.button(
                        label='배송지 변경',
                        key=f'address_{key}',
                        type='primary',
                        disabled=btnStatus.get('addressChange'),
                        width='stretch'
                    )
                    if changeAddrB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page='pages/4myOrder_changeAddr.py')

                    # 주문 상품 상세정보
                    aboutItemB = aboutItem.button(
                        label='상품 상세',
                        key=f'item_{key}',
                        type='primary',
                        width='stretch'
                    )
                    if aboutItemB:
                        st.session_state.item = itemID
                        st.switch_page(page="pages/7item.py")

                    # 주문 상태 변경
                    chagneStatusB = changeStatus.button(
                        label=btnStatus.get('statusChange'),
                        key=f'order_{key}',
                        type='primary',
                        disabled=btnStatus.get('cancelB'),
                        width='stretch'
                    )
                    if chagneStatusB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page=btnStatus.get('switchPagePath'))
        else:
            st.info(body="주문내역 확인 불가")
else:
    st.switch_page(page="mainPage.py")