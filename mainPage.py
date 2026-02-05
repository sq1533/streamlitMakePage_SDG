import streamlit as st
import mimetypes
mimetypes.add_type('text/html', '.html')
mimetypes.add_type('application/javascript', '.js')

import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
import random

utils.init_session()

# item 정보 불러오기 pandas
itemData = api.items.showItem()
vannerData : dict = utils.database().firestore_code
vannerKeys = list(vannerData.keys())

def styled_image(url, height='100%', mobile_height='100%'):
    st.markdown(
        f"""
        <style>
            .fixed-img-container {{
                width: 100%;
                height: {height};
                overflow: hidden;
                border-radius: 4px;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .fixed-img-container img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            @media screen and (max-width: 640px) {{
                .fixed-img-container {{
                    height: {mobile_height} !important;
                    aspect-ratio: auto !important;
                }}
            }}
        </style>
        <div class="fixed-img-container">
            <img src="{url}">
        </div>
        """,
        unsafe_allow_html=True
    )

if 'vanner_selected_key' not in st.session_state or st.session_state.vanner_selected_key not in vannerKeys:
    st.session_state.vanner_selected_key = random.choice(vannerKeys)
    utils.init_session()

selected_key = st.session_state.vanner_selected_key

code_info : dict = utils.database().firestore_code.get(selected_key)
styled_image(utils.utilsDb().logo_base64)
styled_image(str(code_info['path']))

st.divider()

itemList = itemData[itemData['code'] == selected_key]

count_in_card = 0
for i, (index, item) in enumerate(itemList.iterrows()):
    if i % 3 == 0:
        cols = st.columns(spec=3, gap="small", vertical_alignment="top")
    col = cols[i % 3]
    with col.container():
        st.image(str(item['paths'][0]))

        st.markdown(body=f"<div style='font-size: 13px; font-weight: bold;'>{item['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"###### {item['price']:,}원")

        if st.button(
            label='상세보기',
            key=f"loop_item_{index}",
            type='primary',
            width='stretch'
        ):
            st.session_state.item = index
            st.query_params["item_id"] = index
            st.switch_page(page="pages/7item.py")

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    # 회원 소셜 로그인 상태
    if any(value is not None for value in st.session_state.token.values()):
        logoutB = st.button(
            label='sign_out',
            type="secondary",
            width='stretch'
        )
        if logoutB:
            st.session_state.clear()
            st.rerun()

        # 소셜 고객 배송정보 확인
        if st.session_state.user.get('address'):
            pass
        else:
            st.info(body='환영합니다. 배송지 정보를 입력해주세요.')
            time.sleep(2)
            st.switch_page(page='pages/1signIN_address.py')

        myinfo, orderList = st.columns(spec=2, gap="small", vertical_alignment="center")

        myinfo = myinfo.button(
            label='마이페이지',
            type='tertiary',
            width='stretch'
        )
        orderL = orderList.button(
            label='주문내역',
            type='tertiary',
            width='stretch'
        )

        # 마이페이지
        if myinfo:
            st.switch_page(page="pages/3myPage.py")
        # 주문 내역 페이지
        if orderL:
            st.switch_page(page="pages/3myPage_orderList.py")

    # 비회원 상태
    else:
        signIn = st.button(
            label='로그인 / 회원가입',
            type='primary',
            width='stretch'
        )
        if signIn:
            st.switch_page(page="pages/1signIN.py")
    
    utils.set_sidebar()

st.divider()

policyB = st.button(
    label='개인정보 처리방침',
    type='tertiary',
    width='content'
)
cookiesB = st.button(
    label='쿠키 정책',
    type='tertiary',
    width='content'
)
termsB = st.button(
    label='이용약관',
    type='tertiary',
    width='content'
)

if policyB:
    st.switch_page(page='pages/0policy.py')
if cookiesB:
    st.switch_page(page='pages/0cookies.py')
if termsB:
    st.switch_page(page='pages/0useTerms.py')

st.html(body=utils.utilsDb().infoAdmin)