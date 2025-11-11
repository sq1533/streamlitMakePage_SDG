import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=':a:',
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

import utils
import api
import time

# 회원 토큰 세션 및 정보
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

mainVanner : dict = utils.database().firestore_vanner.get('mainVanner')

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
    <img src="{mainVanner.get('path')}" class="fullscreen-gif">
    """
)

# siderbar 정의
with st.sidebar:
    st.title(body='amuredo')

    # 회원 소셜 로그인 상태
    if any(value is not None for value in st.session_state.token.values()):
        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)
        logoutB = st.button(
            label="signOut",
            key='signOut',
            type="secondary",
            use_container_width=True
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
            key='myPage',
            type='tertiary',
            use_container_width=True
        )
        orderL = orderList.button(
            label='주문내역',
            key='orderList',
            type='tertiary',
            use_container_width=True
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
            key='signUPIN',
            type='primary',
            use_container_width=True
        )
        if signIn:
            st.switch_page(page="pages/1signIN.py")

# 네비게이션
sporty, daily, about = st.columns(spec=3, gap='small', vertical_alignment='center')

sportyP = sporty.button(
    label='sporty',
    key='sportyPage',
    type='primary',
    use_container_width=True
)
dailyP = daily.button(
    label='daily',
    key='dailyPage',
    type='primary',
    use_container_width=True
)
aboutP = about.button(
    label='about us',
    key='aboutPage',
    type='secondary',
    use_container_width=True
)

if sportyP:
    st.switch_page(page='pages/9sporty.py')
if dailyP:
    st.switch_page(page='pages/9daily.py')
if aboutP:
    st.switch_page(page='pages/9about.py')

st.divider()

policy, cookies, empty = st.columns(spec=[1,1,3], gap='small', vertical_alignment='center')

policyB = policy.button(
    label='개인정보 처리방침',
    key='policy',
    type='tertiary',
    use_container_width=False
)

cookiesB = cookies.button(
    label='쿠키 정책',
    key='cookiesPolicy',
    type='tertiary',
    use_container_width=False
)

if policyB:
    st.switch_page(page='pages/0policy.py')

if cookiesB:
    st.switch_page(page='pages/0cookies.py')

st.html(body=utils.database().infoAdmin)