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
        st.title(body="상품 주문")

    email : str = str(st.session_state.user.get('email')).split('@', 1)[0]
    item : str = st.session_state.item
    itemInfo = api.items.showItem().loc[item]

    # 홈으로 이동
    goHome = st.button(
        label='HOME',
        type='primary',
        width='content',
        disabled=False
    )
    if goHome:
        st.switch_page(page="mainPage.py")

    st.info(body='결제 시스템 준비중입니다. 네이버페이(미구현) 카카오페이(미구현) 토스페이(테스트 결제)')

    col1, col2 = st.columns(spec=[2,1], gap="small", vertical_alignment="top")

    with col1:
        st.title(body=itemInfo['name'])
        st.markdown(
            body=f'''
            ##### ~~{int((itemInfo['price']*100/(100-itemInfo['discount'])//100)*100):,}~~
            ### :red[{itemInfo['discount']}%] {itemInfo['price']:,}원 
            '''
            )
        st.markdown(body='##### 배송비 :blue[무료배송]')

    col2.image(
        image=str(itemInfo['paths'][0]),
        width='stretch'
        )

    st.markdown(body=f'##### {st.session_state.user.get('address')['home']}')
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
        width='stretch'
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
            now = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now.strftime("%y%m%d%H%M%S")

            raw_order_no = f"{orderTime}{item}{email}"
            orderNo = raw_order_no.ljust(35, '0')[:35]

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

                    # 페이지 전환시, 정보 초기화 방지를 위한 고객 세션 및 결제정보 임시저장
                    try:
                        ref = utils.utilsDb().realtimeDB.reference(path=f'payment_temp/{orderNo}')
                        ref.set({
                            'token':st.session_state.token,
                            'reserveId':reserveId, # reserveId 저장
                            'item':st.session_state.item,
                            'delicomment':st.session_state.get('delicomment'),
                            'user_address':st.session_state.user.get('address').get('home'),
                            'pay_method': 'naver' # 결제 수단 구분
                        })
                        print(f"임시 저장 완료 (Naver): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 실패: {e}")

                    js_code = f"""
                    <script>
                        window.location.href = "{checkoutPage_url}";
                    </script>
                    """
                    components.html(js_code, height=0)

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
            now = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now.strftime("%y%m%d%H%M%S")

            raw_order_no = f"{orderTime}{item}{email}"
            orderNo = raw_order_no.ljust(35, '0')[:35]

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
                        ref = utils.utilsDb().realtimeDB.reference(path=f'payment_temp/{orderNo}')
                        ref.set({
                            'token':st.session_state.token,
                            'tid':tid,
                            'item':st.session_state.item,
                            'delicomment':st.session_state.get('delicomment'),
                            'user_address':st.session_state.user.get('address').get('home'),
                            'pay_method': 'kakao'
                        })
                        print(f"임시 저장 완료 (Kakao): {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 실패: {e}")

                    js_code = f"""
                    <script>
                        window.location.href = "{checkoutPage_url}";
                    </script>
                    """
                    components.html(js_code, height=0)

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

    # 토스페이 결제 요청
    if tosspayBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)
        if itemStatus.get('enable'):
            now = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now.strftime("%y%m%d%H%M%S")

            raw_order_no = f"{orderTime}{item}{email}"
            orderNo = raw_order_no.ljust(35, '0')[:35]

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

                    # 페이지 전환시, 정보 초기화 방지를 위한 고객 세션 및 결제정보 임시저장
                    try:
                        ref = utils.utilsDb().realtimeDB.reference(path=f'payment_temp/{orderNo}')
                        ref.set({
                            'token':st.session_state.token,
                            'payToken':payToken,
                            'item':st.session_state.item,
                            'delicomment':st.session_state.get('delicomment'),
                            'user_address':st.session_state.user.get('address').get('home')
                        })
                        print(f"임시 저장 완료: {orderNo}")
                    except Exception as e:
                        print(f"임시 저장 실패: {e}")
                    
                    js_code = f"""
                    <script>
                        window.location.href = "{checkoutPage_url}";
                    </script>
                    """
                    components.html(js_code, height=0)

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
else:
    st.switch_page(page="mainPage.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)