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

# 회원 토큰 및 정보
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None

dailyVanner : dict = utils.database().firestore_vanner.get('vannerDaily')
itemInfo : dict = api.items.showItem()

keys = []
color = []
series = []
for key, data in itemInfo.items():
    if data.category == 'daily':
        keys.append(key)
        color.append(data.color)
        series.append(data.series)
    else:
        pass

colorPick = list(set(color))
seriesPick = list(set(series))

# 상단 vanner
st.html(
    body=f"""
    <style>
        .fullscreen-gif {{
            width: 100%;
            height: auto;
            aspect-ratio: 21 / 9;
            object-fit: cover;
        }}
    </style>
    <img src="{dailyVanner.get('path')}" class="fullscreen-gif">
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

# 상품 상세페이지 dialog
@st.dialog(title='상품 상세', width='medium')
def showItem(itemID, itemIF):
    itemStatus : dict = api.items.itemStatus(itemId=itemID)
    buyDisable = not itemStatus.get('enable')
    feedT = itemStatus.get('feedback').get('text')

    row1, row2 = st.columns(spec=2, gap='small', vertical_alignment='center')
    with row1.container():
        imgLoad(itemIF['paths'][0])
    with row2.container():
        imgLoad(itemIF['paths'][1])
    with row1.container():
        imgLoad(itemIF['paths'][2])
    with row2.container():
        imgLoad(itemIF['paths'][3])
    # 상품 이름
    st.markdown(f"# {itemIF['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : ~~{int((itemIF['price']*100/(100-itemIF['discount'])//100)*100)}~~:red[-{itemIF['discount']}%] {itemIF['price']}원")

    buyBTN = buy.button(
        label='구매하기',
        key=f'buyItem_{itemID}',
        type='primary',
        disabled=buyDisable,
        width='stretch'
    )
    with st.expander(label="상품 세부정보"):
        info, feed = st.tabs(tabs=['info', '후기'])
        with info:
            imgLoad(itemIF['detail'])
        with feed:
            if feedT.__len__() == 1:
                st.info(body='아직 후기가 없어요...', icon='😪')
            else:
                for i in reversed(feedT[1:]):
                    st.markdown(body=i.keys())
                    st.markdown(body=i.values())

    if buyBTN:
        if any(value is not None for value in st.session_state.token.values()):
            st.session_state.item = itemID
            st.switch_page(page="pages/5orderPage.py")
        else:
            st.error(body='고객이 확인되지 않습니다.')

# siderbar 정의
with st.sidebar:
    st.title(body='amuredo')
    # 고객 로그인 상태 확인
    if any(value is not None for value in st.session_state.token.values()):
        logoutB = st.button(
            label='signOut',
            type='secondary',
            width='stretch'
        )
        if logoutB:
            st.session_state.clear()
            st.rerun()

        # 소셜 고객 배송정보 확인
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

    seriesFilter = st.segmented_control(
        label = "시리즈",
        options = seriesPick,
        selection_mode = "single",
        default = None,
        key="itemSeries",
        label_visibility="visible"
        )

    colorFilter = st.segmented_control(
        label = "컬러",
        options = colorPick,
        selection_mode = "single",
        default = None,
        key="itemColor",
        label_visibility="visible"
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

count_in_card = 0
line = keys.__len__()//4 + 1

# 아이템에 따른 행 갯수 수정
for l in range(line):
    cards = st.columns(spec=4, gap="small", vertical_alignment="top")

# 아이템 4열 배치
for itemKey in keys:
    itemCard : dict = itemInfo.get(itemKey)
    if (colorFilter == None or colorFilter in itemCard.get('color')) and (seriesFilter == None or seriesFilter in itemCard.get('series')):
        with cards[count_in_card].container():
            itemStatus : dict = api.items.itemStatus(itemId=itemKey)
            feedback : dict = itemStatus.get('feedback')

            imgLoad(itemCard['paths'][0])

            st.markdown(body=f"###### {itemCard.get('name')}")
            st.markdown(body=f':heart: {feedback.get('point')}')

            viewBTN = st.button(
                label="상세보기",
                key=f"loop_item_{itemKey}",
                type="primary",
                width='stretch'
            )
            if viewBTN:
                showItem(itemID=itemKey, itemIF=itemCard)

        count_in_card += 1
        if count_in_card == 4:
            count_in_card = 0
        else:
            pass
    else:
        pass

st.divider()

policy, cookies, empty = st.columns(spec=[1,1,3], gap='small', vertical_alignment='center')

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

if policyB:
    st.switch_page(page='pages/0policy.py')

if cookiesB:
    st.switch_page(page='pages/0cookies.py')

st.html(body=utils.database().infoAdmin)