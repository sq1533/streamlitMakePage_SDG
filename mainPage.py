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

st.markdown(
    """
    <div style='text-align: center; padding: 2rem 0;'>
        <h2 style='color: #121212; font-weight: 800; font-family: "Outfit", sans-serif;'>업무의 효율을 높이는 안경, AMUREDO</h2>
        <p style='color: #555555; font-size: 1.1rem; margin-top: 0.5rem;'>
            모니터 앞에서의 긴 시간, 당신의 눈과 집중력을 지켜줄 사무용 안경 컬렉션
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

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
            type='secondary',
            width='stretch'
        ):
            st.session_state.page['item'] = index
            st.session_state.page['page'] = 'pages/7item.py'
            st.switch_page(page="pages/7item.py")

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0; color: #555;'>
            <em>Office Eyewear<br>for Professionals</em>
        </div>
        """,
        unsafe_allow_html=True
    )

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