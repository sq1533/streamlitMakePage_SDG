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
import pandas as pd

utils.init_session()

if st.session_state.page == 'sporty':
    page = {'vanner':'vannerSporty', 'category':'sporty'}
elif st.session_state.page == 'daily':
    page = {'vanner':'vannerDaily', 'category':'daily'}
elif st.session_state.page == 'glasses':
    page = {'vanner':'vannerDaily', 'sort':'glasses'}
elif st.session_state.page == 'sunglasses':
    page = {'vanner':'vannerDaily', 'sort':'sunglasses'}
else:
    st.switch_page(page='mainPage.py')

index = list(page.keys())[1]

# 페이지 배너 가져오기
vanner : dict = utils.utilsDb().firestore_vanner.get(page.get('vanner'))
# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData[index] == page.get(index)]

itemID = itemData.index.tolist()

all_status = api.items.getAllItemStatus()
itemData['sales'] = itemData.index.map(
    lambda x: all_status.get(x, {}).get('sales', 0)
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
            st.toast("기본 배송지 설정 필요", icon="⚠️")
            time.sleep(0.7)
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

    st.markdown(
        """
        <style>
        /* 라디오 버튼의 옵션 텍스트(label) 스타일링 */
        [data-testid="stRadio"] div[role="radiogroup"] label {
            font-size:1.2rem;
            border:1px solid #8D6E63;  /* 테두리 추가 */
            border-radius:8px;         /* 모서리 둥글게 */
            padding:10px;              /* 텍스트와 테두리 사이 여백 */
            margin-bottom:5px;         /* 항목 간 간격 */
            width:100%;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    sortedFilter = st.radio(
        label='정렬',
        options=['New', '인기순', '낮은 가격순', '높은 가격순'],
        label_visibility='collapsed'
    )

count_in_card = 0
line = itemID.__len__()//3 + 1

# 아이템에 따른 행 갯수 수정
for l in range(line):
    cards = st.columns(spec=3, gap="small", vertical_alignment="top")

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

# 아이템 3열 배치
for index, item in sortedItems.iterrows():
    with cards[count_in_card].container():
        itemStatus : dict = api.items.itemStatus(itemId=index)
        feedback : dict = itemStatus.get('feedback')

        st.image(
            image=str(item['paths'][0]),
            output_format='JPEG'
        )

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
    if count_in_card == 3:
        count_in_card = 0
    else:
        pass

st.divider()

st.html(body=utils.utilsDb().infoAdmin)