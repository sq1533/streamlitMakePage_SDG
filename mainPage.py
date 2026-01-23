import streamlit as st
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

utils.init_session()

mainVanner : dict = utils.utilsDb().firestore_vanner.get('vannerMain')

# 상단 vanner
st.html(
    body=f"""
    <style>
        .banner-video {{
            width: 100%;
            height: auto;
            aspect-ratio: 21 / 9;
            object-fit: cover;
        }}
    </style>
    <video
        class="banner-video"
        autoplay
        muted
        loop
        playsinline 
        poster="{mainVanner.get('path')}">

        <source src="{mainVanner.get('video_webm')}" type="video/webm">
        <source src="{mainVanner.get('video_mp4')}" type="video/mp4">
    </video>
    """
)

# item 정보 불러오기 pandas
itemData = api.items.showItem()
itemData = itemData[itemData['event'] == 'best']

glassesData = itemData[itemData['sort'] == 'glasses'].copy()
sunglassesData = itemData[itemData['sort'] == 'sunglasses'].copy()

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

line01, subtitle, line02 = st.columns(spec=3, gap='small', vertical_alignment='center')
line01.divider()
subtitle.markdown(
    body="<h3 style='text-align: center;'>recommend for you</h3>",
    unsafe_allow_html=True
    )
line02.divider()

# glassesData의 sort행 상위 3개
count_in_card = 0
bestGlasses = glassesData.sort_index()

for i, (index, item) in enumerate(bestGlasses.iterrows()):
    if i % 3 == 0:
        cols = st.columns(spec=3, gap="small", vertical_alignment="top")
    col = cols[i % 3]
    with col.container():
        thumb_img = utils.load_and_optimize_from_url(str(item['paths'][0]), quality=80)
        if thumb_img:
            st.image(thumb_img, output_format='WEBP')
        else:
            st.image(str(item['paths'][0]), output_format='JPEG')

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

# sunglassesData의 sort행 상위 3개
count_in_card = 0
bestSunglasses = sunglassesData.sort_index()


for i, (index, item) in enumerate(bestSunglasses.iterrows()):
    if i % 3 == 0:
        cols = st.columns(spec=3, gap="small", vertical_alignment="top")
    col = cols[i % 3]
    with col.container():
        thumb_img = utils.load_and_optimize_from_url(str(item['paths'][0]), quality=80)
        if thumb_img:
            st.image(thumb_img, output_format='WEBP')
        else:
            st.image(str(item['paths'][0]), output_format='JPEG')

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

    count_in_card += 1

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