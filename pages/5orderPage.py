import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
from datetime import datetime, timezone, timedelta
import streamlit.components.v1 as components

utils.init_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.item:

    with st.sidebar:
        st.page_link(
            page='mainPage.py',
            label='AMUREDO'
        )
        st.title(body="상품 주문")

        utils.set_sidebar()

    email : str = str(st.session_state.user.get('email')).split('@', 1)[0]
    item : str = st.session_state.item
    itemInfo = api.items.showItem().loc[item]

    st.info(body='네이버페이, 신용카드 결제 준비중입니다.')

    col1, col2 = st.columns(spec=[2,1], gap="small", vertical_alignment="top")

    with col1:
        st.title(body=itemInfo['name'])
        st.markdown(
            body=f"""
            ### {itemInfo['price']:,}원 
            """
            )
        st.markdown(body='##### 배송비 :blue[무료배송]')

    col2.image(
        image=str(itemInfo['paths'][0]),
        width='stretch'
        )

    deliveryAddress = st.selectbox(
        label='배송지',
        options=st.session_state.user.get('address').values(),
        index=len(st.session_state.user.get('address').values()) - 1
    )
    st.text_input(
        label='배송 요청사항',
        value=None,
        max_chars=100,
        key='delicomment',
        placeholder='배송 요청사항을 입력해주세요.'
    )

    # 버튼 스타일 변경 분기점
    st.markdown('<div id="pay-section-marker"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <style>
        /* 1번 네이버페이 (초록) */
        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(1) button {
            background-color: #03C75A !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }
        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(1) button:hover {
            background-color: #02B350 !important;
        }

        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(2) button {
            background-color: #FEE500 !important;
            color: #191919 !important;
            border: none !important;
            font-weight: bold !important;
        }
        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(2) button:hover {
            background-color: #E6CE00 !important;
        }

        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(3) button {
            background-color: #0064FF !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
        }
        div:has(#pay-section-marker) ~ div div[data-testid="stColumn"]:nth-of-type(3) button:hover {
            background-color: #0050CC !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    naverpay, kakaopay, tosspay = st.columns(spec=3, gap='small', vertical_alignment='center')

    naverpayBTN = naverpay.button(
        label='Naver Pay',
        type='primary',
        width='stretch',
        disabled=True
        )
    kakaopayBTN = kakaopay.button(
        label='kakao Pay',
        type='primary',
        width='stretch'
        )
    tosspayBTN = tosspay.button(
        label='Toss Pay', 
        type='primary', 
        width='stretch'
    )

    # 네이버페이 결제 요청
    if naverpayBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)
        if itemStatus.get('enable'):
            now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now_kst.strftime("%y%m%d%H%M%S")

            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
                raw_order_no = f"{orderTime}{item}{email}"
                orderNo = raw_order_no.ljust(35, '0')[:35]
                callNaverpay : dict = api.pay().naverpayToken(
                    orderNo=orderNo,
                    itemName=itemInfo['name'],
                    amount=int(itemInfo['price'])
                    )
                
                if callNaverpay.get('access'):
                    reserveId : str = callNaverpay.get('reserveId')
                    checkoutPage_url = callNaverpay.get('checkoutPage_url')

                    # 결제 방법 및 고유값 업데이트
                    try:
                        ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{orderNo}")
                        ref.update({
                            'token': st.session_state.token,
                            'item': item,
                            'delicomment': st.session_state.get('delicomment'),
                            'user_address': deliveryAddress,
                            'reserveId': reserveId,
                            'pay_method': 'naver'
                        })
                        print(f"임시 저장 업데이트 (Naver): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 업데이트 실패 (Naver): {e}")

                    st.markdown(
                        body=f"<meta http-equiv='refresh' content='0;url={checkoutPage_url}'>",
                        unsafe_allow_html=True
                        )

                    st.link_button("결제창이 자동으로 열리지 않으면 클릭하세요", checkoutPage_url)
                else:
                    # 토큰 발급 실패 시 예약 취소
                    api.items.cancelReservation(st.session_state.token, item, orderTime)
                    st.toast(f"결제 생성 실패: {callNaverpay.get('message')}", icon="❌")
                    time.sleep(1)
                    if 'item' in st.session_state:
                        del st.session_state.item
                    st.rerun()
            else:
                 st.warning("재고가 부족하여 주문할 수 없습니다. (Sold Out)")
                 time.sleep(2)
                 if 'item' in st.session_state:
                    del st.session_state.item
                 st.rerun()
        else:
            st.toast('상품 구매가 불가합니다 - soldout', icon="⚠️")
            time.sleep(1)
            if 'item' in st.session_state:
                del st.session_state.item
            st.rerun()

    if kakaopayBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)

        if itemStatus.get('enable'):
            now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now_kst.strftime("%y%m%d%H%M%S")

            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
                raw_order_no = f"{orderTime}{item}{email}"
                orderNo = raw_order_no.ljust(35, '0')[:35]

                callKakaopay : dict = api.pay().kakaopayToken(
                    orderNo=orderNo,
                    itemName=itemInfo['name'],
                    amount=int(itemInfo['price'])
                    )
                
                if callKakaopay.get('access'):
                    tid : str = callKakaopay.get('tid')
                    checkoutPage_url = callKakaopay.get('checkoutPage')

                    try:
                        ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{orderNo}")
                        ref.update({
                            'token': st.session_state.token,
                            'item': item,
                            'delicomment': st.session_state.get('delicomment'),
                            'user_address': deliveryAddress,
                            'tid': tid,
                            'pay_method': 'kakao'
                        })
                        print(f"임시 저장 업데이트 (Kakao): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 업데이트 실패 (Kakao): {e}")

                    st.markdown(
                        body=f"<meta http-equiv='refresh' content='0;url={checkoutPage_url}'>",
                        unsafe_allow_html=True
                        )

                    st.link_button("결제창이 자동으로 열리지 않으면 클릭하세요", checkoutPage_url)
                else:
                    api.items.cancelReservation(st.session_state.token, item, orderTime)
                    st.toast(f"결제 생성 실패: {callKakaopay.get('message')}", icon="❌")
                    time.sleep(1)
                    if 'item' in st.session_state:
                        del st.session_state.item
                    st.rerun()
            else:
                 st.warning("재고가 부족하여 주문할 수 없습니다. (Sold Out)")
                 time.sleep(2)
                 if 'item' in st.session_state:
                    del st.session_state.item
                 st.rerun()
        else:
            st.toast('상품 구매가 불가합니다 - soldout', icon="⚠️")
            time.sleep(1)
            if 'item' in st.session_state:
                del st.session_state.item
            st.rerun()

    # 토스페이(간편) 결제 요청
    if tosspayBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)

        if itemStatus.get('enable'):
            now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now_kst.strftime("%y%m%d%H%M%S")

            # 재고 예약
            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
                raw_order_no = f"{orderTime}{item}{email}"
                orderNo = raw_order_no.ljust(35, '0')[:35]

                # 토스 페이 토큰 발급
                callTosspayToken : dict = api.pay().tosspayToken(
                    orderNo=orderNo,
                    itemName=itemInfo['name'],
                    amount=int(itemInfo['price'])
                    )
                
                if callTosspayToken.get('access'):
                    payToken : str = callTosspayToken.get('payToken')
                    checkoutPage_url : str = callTosspayToken.get('checkoutPage')

                    try:
                        ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{orderNo}")
                        ref.update({
                            'token': st.session_state.token,
                            'item': item,
                            'delicomment': st.session_state.get('delicomment'),
                            'user_address': deliveryAddress,
                            'payToken': payToken,
                            'pay_method': 'toss_simple'
                        })
                        print(f"임시 저장 업데이트 (toss): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 업데이트 실패 (toss): {e}")
                        if 'item' in st.session_state:
                            del st.session_state.item
                        st.rerun()
                    st.markdown(
                        body=f"<meta http-equiv='refresh' content='0;url={checkoutPage_url}'>",
                        unsafe_allow_html=True
                        )

                    st.link_button("결제창이 자동으로 열리지 않으면 클릭하세요", checkoutPage_url)
                else:
                    # 토큰 발급 실패 시 예약 취소
                    api.items.cancelReservation(st.session_state.token, item, orderTime)
                    st.toast(f"결제 생성 실패: {callTosspayToken.get('message')}", icon="❌")
                    time.sleep(1)
                    if 'item' in st.session_state:
                        del st.session_state.item
                    st.rerun()
            else:
                st.toast("재고가 부족하여 주문할 수 없습니다. (Sold Out)", icon="⚠️")
                time.sleep(1)
                if 'item' in st.session_state:
                    del st.session_state.item
                st.rerun()

        else:
            st.toast('상품 구매가 불가합니다 - soldout', icon="⚠️")
            time.sleep(1)
            if 'item' in st.session_state:
                del st.session_state.item
            st.rerun()

    cardBTN = st.button(
        label='신용카드',
        type='secondary',
        icon='💳',
        width='stretch'
    )

    if cardBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)

        if itemStatus.get('enable'):
            now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now_kst.strftime("%y%m%d%H%M%S")

            # 재고 예약
            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
                raw_order_no = f"{orderTime}{item}{email}"
                orderNo = raw_order_no.ljust(35, '0')[:35]
                try:
                    ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{orderNo}")
                    ref.update({
                        'token': st.session_state.token,
                        'item': item,
                        'delicomment': st.session_state.get('delicomment'),
                        'user_address': deliveryAddress,
                        'pay_method': 'toss_widget'
                    })
                    st.session_state.orderNo = orderNo
                    st.switch_page(page="pages/5pay_tosspayments.py")
                except Exception as e:
                    print(f"임시 저장 업데이트 실패 (tosspayments): {e}")
                    if 'item' in st.session_state:
                        del st.session_state.item
                    st.rerun()
else:
    st.switch_page(page="mainPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)