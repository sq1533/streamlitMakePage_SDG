import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
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
import requests
import time
from datetime import datetime, timezone, timedelta

utils.init_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.item:
    with st.sidebar:
        st.title(body="상품 주문")

    item : str = st.session_state.item
    itemInfo = api.items.showItem().loc[item]

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
            use_container_width=True
        )

        if tosspayBTN:
            itemStatus : dict = api.items.itemStatus(itemId=item)
            if itemStatus.get('enable'):
                # 고객 주문 key == 주문 시간
                now = datetime.now(timezone.utc) + timedelta(hours=9)
                orderTime = now.strftime("%y%m%d%H%M%S")
                orderNo = f'{orderTime}{item}{st.session_state.user.get('email')[:10]}'
                # 토스 페이 토큰 발급
                callTosspayToken : dict = api.pay().tosspayToken(
                    orderNo=orderNo,
                    itemName=itemInfo['name'],
                    amount=int(itemInfo['price'])
                    )
                
                if callTosspayToken.get('access'):
                    st.session_state.payToken : str = callTosspayToken.get('payToken')
                    checkoutPage_url : str = callTosspayToken.get('checkoutPage')
                    st.markdown(
                        body=f'<meta http-equiv="refresh" content="0;url={checkoutPage_url}">',
                        unsafe_allow_html=True
                        )

                    st.info("결제창으로 이동합니다. 이동하지 않으면 아래 링크를 클릭하세요.")
                    st.link_button("결제창 열기", checkoutPage_url)
                else:
                    st.warning(f"결제 생성 실패: {callTosspayToken.get('message')}")
                    time.sleep(2)
                    st.session_state.item = None
                    st.rerun()
            else:
                st.warning(body='상품 구매가 불가합니다 - soldout')
                time.sleep(2)
                st.session_state.item = None
                st.rerun()
else:
    st.switch_page(page="mainPage.py")

st.divider()
st.html(body=utils.database().infoAdmin)

### 결과 url -- https://localhost:8080/orderPage?status=PAY_APPROVED&orderNo=251216162437sporty002618356@nav&payMethod=TOSS_MONEY&bankCode=092