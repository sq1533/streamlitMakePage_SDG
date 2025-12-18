import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
from datetime import datetime, timezone, timedelta

utils.init_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()) and st.session_state.item:
    with st.sidebar:
        st.title(body="상품 주문")

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

    # 토스페이 결제 요청
    if tosspayBTN:
        itemStatus : dict = api.items.itemStatus(itemId=item)
        if itemStatus.get('enable'):
            # 고객 주문 key == 주문 시간
            now = datetime.now(timezone.utc) + timedelta(hours=9)
            orderTime = now.strftime("%y%m%d%H%M%S")
            
            # orderNo 생성
            email = str(st.session_state.user.get('email')).split('@', 1)[0]
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

                # 페이지 전환시, 정보 초기화 방지를 위한 고객 세션 및 결제정보 임시저장
                try:
                    ref = utils.database().realtimeDB.reference(path=f'payment_temp/{orderNo}')
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
                
                # 토스페이 결제창 전환
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