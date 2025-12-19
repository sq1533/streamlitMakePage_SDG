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
glassesData = itemData[itemData['sort'] == 'glasses']
sunglassesData = itemData[itemData['sort'] == 'sunglasses']

all_status = api.items.getAllItemStatus()
glassesData['sales'] = glassesData.index.map(
    lambda x: all_status.get(x, {}).get('sales', 0)
)
sunglassesData['sales'] = sunglassesData.index.map(
    lambda x: all_status.get(x, {}).get('sales', 0)
)

# siderbar 정의
with st.sidebar:
    st.title(body='amuredo')

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

    st.divider()

    st.markdown(body='### 무엇을 찾으시나요?')

    glassesBTN = st.button(
        label='glasses',
        type='tertiary',
        icon=':material/eyeglasses_2:',
        width='content'
    )
    sunglassesBTN = st.button(
        label='sunglasses',
        type='tertiary',
        icon=':material/sunny:',
        width='content'
    )

    if glassesBTN:
        st.session_state.page = 'glasses'
        st.switch_page(page='pages/9itemList.py')
    if sunglassesBTN:
        st.session_state.page = 'sunglasses'
        st.switch_page(page='pages/9itemList.py')

    st.divider()

    st.markdown(body='### Information')

    st.page_link(
        page='pages/0notice.py',
        label='이벤트 및 공지사항',
        icon='📢',
        help='놓치면 후회할 특별한 혜택!'
    )

    st.page_link(
        page='pages/0cs.py',
        label='문의하기',
        icon='🎧'
    )

# 네비게이션
daily, sporty, about = st.columns(spec=3, gap='small', vertical_alignment='center')

dailyP = daily.button(
    label='daily',
    type='secondary',
    width='stretch'
)
sportyP = sporty.button(
    label='sporty',
    type='secondary',
    width='stretch'
)
aboutP = about.button(
    label='about us',
    type='secondary',
    width='stretch'
)

if dailyP:
    st.session_state.page = 'daily'
    st.switch_page(page='pages/9itemList.py')
if sportyP:
    st.session_state.page = 'sporty'
    st.switch_page(page='pages/9itemList.py')
if aboutP:
    st.switch_page(page='pages/9about.py')

st.divider()

# glassesData의 sort행 상위 3개
st.markdown(body='### :orange[Best] Glasses')
count_in_card = 0
cards = st.columns(spec=3, gap="small", vertical_alignment="top")
bestGlasses = glassesData.sort_values(by='sales', ascending=False).head(3)

for index, item in bestGlasses.iterrows():
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

# sunglassesData의 sort행 상위 3개
st.markdown(body='### :orange[Best] Sunglasses')

count_in_card = 0
cards = st.columns(spec=3, gap="small", vertical_alignment="top")
bestSunglasses = sunglassesData.sort_values(by='sales', ascending=False).head(3)

for index, item in bestSunglasses.iterrows():
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