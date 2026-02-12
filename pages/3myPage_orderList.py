import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
from datetime import datetime

# 페이지 진입 확인
if not any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page="mainPage.py")

with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()

st.markdown(body="주문내역")

userOrder : dict = st.session_state.user.get('orderList')

if userOrder:
    # 아이템 정보 호출
    itemInfo = api.items.showItem()

    for key, order in reversed(st.session_state.user.get('orderList').items()):
        # 주문 정보
        orderTime = key
        itemID = order.get('item')
        address = order.get('address')
        comment = order.get('comment')
        feedback = order.get('feedback')
        status = utils.utilsDb().showStatus[order.get('status')]

        # 상품
        itemIF = itemInfo.loc[itemID]

        with st.expander(label=f"주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemIF['name']} {status}"):
            # 상품 이미지, 정보 호출
            image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
            with image.container():
                st.image(
                    image=str(itemIF['paths'][0]),
                    output_format='JPEG'
                )
            with info.container():
                st.markdown(body=f"##### {itemIF['name']}")
                st.markdown(body=f"##### {address}")
                if comment:
                    st.markdown(body=f"##### {comment}")
                else:
                    pass

            # 후기 유무 검사
            if feedback:
                fbDisable = True
            else:
                fbDisable = False

            # 후기 입력
            feedT, feed, feedB = st.columns(spec=[2,1,1], gap='small', vertical_alignment='center')
            fdt = feedT.text_input(
                label='후기 남기기',
                value=None,
                max_chars=20,
                key=f"feedText_{key}",
                placeholder='상품은 어떠셨나요?',
                disabled=fbDisable,
                label_visibility='collapsed'
            )
            fbing = feed.feedback(
                options='thumbs',
                key=f"itemFB_{key}",
                disabled=fbDisable
                )
            fbB = feedB.button(
                label='평가',
                key=f"feedbackAdd_{key}",
                type='secondary',
                disabled=fbDisable,
                width='stretch'
            )
            if fbB:
                if fbing:
                    feadbackDone = api.items.addFeedback(token=st.session_state.token, key=orderTime, itemID=itemID, feedback=fbing, feedT=fdt)
                    if feadbackDone:
                        st.toast('소중한 의견 감사합니다.', icon="✅")
                        time.sleep(0.7)
                        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
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
            elif order.get('status') == 'exchange': # 교환 요청 > 배송지 변경 불가, 주문 상태 변경 불가
                btnStatus = {
                    'addressChange' : True,
                    'cancelB' : True,
                    'statusChange' : '교환 진행 중..',
                    'switchPagePath' : 'mainPage.py'
                }
            else: # 상품 배송중 or 상품 배송완료( 7일 경과 전 )
                btnStatus = {
                    'addressChange' : True,
                    'cancelB' : False,
                    'statusChange' : '교환 및 환불',
                    'switchPagePath' : 'pages/4myOrder_itemRefund.py'
                }

            # 주문 상품 배송지 변경
            changeAddrB = changeAddr.button(
                label='배송지 변경',
                key=f"address_{key}",
                type='secondary',
                disabled=btnStatus.get('addressChange'),
                width='stretch'
            )
            if changeAddrB:
                st.session_state.page['orderItem'] = [key, order]
                st.switch_page(page='pages/4myOrder_changeAddr.py')

            # 주문 상품 상세정보
            aboutItemB = aboutItem.button(
                label='상품 상세',
                key=f"item_{key}",
                type='secondary',
                width='stretch'
            )
            if aboutItemB:
                st.session_state.page['item'] = itemID
                st.switch_page(page="pages/7item.py")

            # 주문 상태 변경
            chagneStatusB = changeStatus.button(
                label=btnStatus.get('statusChange'),
                key=f"order_{key}",
                type='secondary',
                disabled=btnStatus.get('cancelB'),
                width='stretch'
            )
            if chagneStatusB:
                st.session_state.page['orderItem'] = [key, order]
                st.switch_page(page=btnStatus.get('switchPagePath'))

else:
    st.info(body="주문내역 확인 불가")