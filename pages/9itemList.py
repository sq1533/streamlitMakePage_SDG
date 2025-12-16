import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
st.html(
    """
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    video::-webkit-media-controls {
        display: none !important;
    }
    video {
        width: 100% !important;
        aspect-ratio: 20 / 9;
        object-fit: fill;
    }
    </style>
    """
)

import api
import time
import pandas as pd

utils.init_session()

if st.session_state.page == 'sporty':
    page = {'vanner':'vannerSporty', 'category':'sporty'}
elif st.session_state.page == 'daily':
    page = {'vanner':'vannerDaily', 'category':'daily'}
else:
    st.switch_page(page='mainPage.py')

# 페이지 배너 가져오기
vanner : dict = utils.database().firestore_vanner.get(page.get('vanner'))
# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData['category'].str.contains(page.get('category'), case=False, na=False)]

itemID = itemData.index.tolist()

all_status = api.items.getAllItemStatus()
itemData['sales'] = itemData.index.map(
    lambda x: all_status.get(x, {}).get('sales', 0)
)

itemData['point'] = itemData.index.map(
    lambda x: all_status.get(x, {}).get('feedback', {}).get('point', 0)
)

# 홈으로 이동
goHome = st.button(
    label='HOME',
    type='primary',
    width='content',
    disabled=False
)
if goHome:
    st.switch_page(page="mainPage.py")

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
        poster="{vanner.get('path')}">

        <source src="{vanner.get('video_webm')}" type="video/webm">
        <source src="{vanner.get('video_mp4')}" type="video/mp4">
    </video>
    """
)

def imgLoad(path : str):
    if path:
        return st.image(
            image=path,
            output_format='JPEG'
        )
    else:
        return st.info(body='not image')

# siderbar 정의
with st.sidebar:
    st.title(body='amuredo')
    # 회원 로그인 상태 확인
    if any(value is not None for value in st.session_state.token.values()):
        logoutB = st.button(
            label='sign_out',
            type='secondary',
            width='stretch'
        )
        if logoutB:
            st.session_state.clear()
            st.rerun()

        if st.session_state.user.get('address'):
            pass
        else:
            st.info(body='기본 배송지 설정 필요')
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
    else:
        signIn = st.button(
            label='로그인 / 회원가입',
            type='primary',
            width='stretch'
        )
        if signIn:
            st.switch_page(page="pages/1signIN.py")

    sortedFilter = st.segmented_control(
        label='정렬',
        options=['New', '인기순', '낮은 가격순', '높은 가격순'],
        selection_mode='single',
        default = None,
        label_visibility='visible'
        )

count_in_card = 0
line = itemID.__len__()//4 + 1

# 아이템에 따른 행 갯수 수정
for l in range(line):
    cards = st.columns(spec=4, gap="small", vertical_alignment="top")

# 상품 정렬을 위한 키 리스트 정리
if sortedFilter == 'New':
    sortedItems = itemData.sort_values(by='created_at', ascending=False)
elif sortedFilter == '인기순':
    sortedItems = itemData.sort_values(by='sales', ascending=False)
elif sortedFilter == '낮은 가격순':
    sortedItems = itemData.sort_values(by='price', ascending=True)
elif sortedFilter == '높은 가격순':
    sortedItems = itemData.sort_values(by='price', ascending=False)
else:
    sortedItems = itemData

# 아이템 4열 배치
for index, item in sortedItems.iterrows():
    with cards[count_in_card].container():
        itemStatus : dict = api.items.itemStatus(itemId=index)
        feedback : dict = itemStatus.get('feedback')

        imgLoad(str(item['paths'][0]))

        st.markdown(body=f"###### {item['name']} :heart: {feedback.get('point', 0)}")
        st.markdown(f"###### :red[{item['discount']}%] {item['price']:,}원")

        viewBTN = st.button(
            label='상세보기',
            key=f'loop_item_{index}',
            type='primary',
            width='stretch'
        )
        if viewBTN:
            st.session_state.item = index
            st.switch_page(page="pages/7item.py")

    count_in_card += 1
    if count_in_card == 4:
        count_in_card = 0
    else:
        pass

st.divider()

policy, cookies, terms, empty = st.columns(spec=[1,1,1,2], gap='small', vertical_alignment='center')

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

st.html(body=utils.database().infoAdmin)