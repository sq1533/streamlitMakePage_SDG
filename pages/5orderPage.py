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
from api.tosspay_widget import render_payment_widget
from api.tosspay_handler import handle_payment_callback
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

    st.info(body='네이버페이 준비중입니다.')

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

    if 'orderNo' not in st.session_state:
        now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
        orderTime = now_kst.strftime("%y%m%d%H%M%S")

        raw_order_no = f"{orderTime}{item}{email}"
        orderNo = raw_order_no.ljust(35, '0')[:35]

    try:
        ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{orderNo}")
        ref.update({
            'token': st.session_state.token,
            'item': st.session_state.item,
            'delicomment': st.session_state.get('delicomment'),
            'user_address': deliveryAddress,
            'created_at': str(datetime.now(timezone.utc))
        })
    except Exception as e:
        print(f"공통 임시 저장 실패: {e}")

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

            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
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
            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
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

            # 재고 예약
            reserved = api.items.reserveItem(
                token=st.session_state.token,
                itemID=item,
                orderTime=orderTime
            )

            if reserved:
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
                            'payToken': payToken,
                            'pay_method': 'toss_simple'
                        })
                        print(f"임시 저장 업데이트 (toss): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 업데이트 실패 (toss): {e}")
                    
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

    # ----------------------------------------------------------------------
    # [토스페이먼츠 위젯] (일반결제) - 신용카드 등
    # ----------------------------------------------------------------------
    st.divider()
    st.subheader("일반 결제 (신용카드/가상계좌 등)")

    try:
        toss_client_key = st.secrets["tosspayments"]["client_key"]
    except Exception:
        toss_client_key = "TEST_CLIENT_KEY"

    # 위젯은 별도 버튼 클릭 없이 JS단에서 처리되므로, 
    # 공통 저장 로직(`st.session_state.orderNo`)을 그대로 사용.
    # 단, pay_method는 위젯 로딩 시 'toss_widget'으로 마킹해두거나 성공 후 페이지에서 처리 가능.
    # 여기서는 명시적으로 update 한번 더 해줌 (선택 사항)
    try:
        ref = utils.utilsDb().realtimeDB.reference(path=f"payment_temp/{st.session_state.orderNo}")
        ref.update({'pay_method': 'toss_widget'})
    except:
        pass

    render_payment_widget(
        client_key=toss_client_key,
        customer_key=email, 
        amount=int(itemInfo['price']),
        order_id=st.session_state.orderNo, # 공통 주문 번호 사용
        order_name=itemInfo['name'],
        customer_email=email,
        customer_name=st.session_state.user.get('name', '고객'),
        success_url="https://amuredo.shop/5pay_tosspayments", 
        fail_url="https://amuredo.shop/5pay_tosspayments",
        height=600
    )
else:
    st.switch_page(page="mainPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)