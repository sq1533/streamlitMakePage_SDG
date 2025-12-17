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
utils.set_page_ui()

import api
import time

utils.init_session()

mainVanner : dict = utils.database().firestore_vanner.get('vannerMain')

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
    # sporty 및 daily 하위모델( new, best 필터 적용 페이지 switch 버튼 )
    # st.session_state.sort = 'new'

    st.divider()

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
sporty, daily, about = st.columns(spec=3, gap='small', vertical_alignment='center')

sportyP = sporty.button(
    label='sporty',
    type='primary',
    width='stretch'
)
dailyP = daily.button(
    label='daily',
    type='primary',
    width='stretch'
)
aboutP = about.button(
    label='about us',
    type='secondary',
    width='stretch'
)

if sportyP:
    st.session_state.page = 'sporty'
    st.switch_page(page='pages/9itemList.py')
if dailyP:
    st.session_state.page = 'daily'
    st.switch_page(page='pages/9itemList.py')
if aboutP:
    st.switch_page(page='pages/9about.py')

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