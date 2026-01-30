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

st.markdown("""
<style>
@media screen and (max-width: 640px) {
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
    }
    div[data-testid="stColumn"] {
        min-width: 0px !important;
        width: auto !important;
    }
}
</style>
""", unsafe_allow_html=True)

# item 정보 불러오기 pandas
itemData = api.items.showItem()
vannerData : dict = utils.utilsDb().firestore_vanner

def styled_image(url, height='100vw', mobile_height='100vw'):
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

vannerKeys = [key for key in vannerData.keys() if key != 'txt']
selected_key = random.sample(vannerKeys, 1)[0]
txtImg = vannerData.get('txt')['path']
item_img_url = vannerData.get(selected_key)['path']

img, txt = st.columns(spec=[2,1], gap='small', vertical_alignment='top')
with img.container():
    styled_image(url=item_img_url)
with txt.container():
    styled_image(url=txtImg)

itemCode = itemData.loc[selected_key]['code']
itemList = itemData[itemData['code'] == itemCode]

st.divider()

count_in_card = 0
for i, (index, item) in enumerate(itemList.iterrows()):
    if i % 3 == 0:
        cols = st.columns(spec=3, gap="small", vertical_alignment="top")
    col = cols[i % 3]
    with col.container():
        st.image(str(item['paths'][0]))

        st.markdown(body=f"###### {item['name']}")
        st.markdown(f"###### {item['price']:,}원")

        if st.button(
            label='상세보기',
            key=f"loop_item_{index}",
            type='primary',
            width='stretch'
        ):
            st.session_state.item = index
            st.switch_page(page="pages/7item.py")

# siderbar 정의
with st.sidebar:
    st.page_link(
        page='mainPage.py',
        label='AMUREDO'
    )

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

policy, cookies, terms = st.columns(spec=3, gap='small', vertical_alignment='center')

policyB = policy.button(
    label='개인정보 처리방침',
    type='tertiary',
    width='content'
)
cookiesB = cookies.button(
    label='쿠키 정책',
    type='tertiary',
    width='content'
)
termsB = terms.button(
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