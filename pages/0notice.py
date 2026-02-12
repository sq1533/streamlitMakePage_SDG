import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

# 공지 상세보기 세션 구분
if 'selected_notice' not in st.session_state:
    st.session_state.selected_notice = None

with st.sidebar:
    utils.set_sidebarLogo()
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
            st.session_state.page['page'] = 'pages/3myPage.py'
            st.switch_page(page=f"{st.session_state.page['page']}")
        # 주문 내역 페이지
        if orderL:
            st.session_state.page['page'] = 'pages/3myPage_orderList.py'
            st.switch_page(page=f"{st.session_state.page['page']}")

    # 비회원 상태
    else:
        signIn = st.button(
            label='로그인 / 회원가입',
            type='secondary',
            width='stretch'
        )
        if signIn:
            st.switch_page(page='pages/1signIN.py')

    utils.set_sidebar()

# 홈으로 이동
goHome = st.button(
    label='HOME',
    type='secondary',
    width='content',
    disabled=False
)
if goHome:
    st.session_state.page['page'] = 'mainPage.py'
    st.switch_page(page=f"{st.session_state.page['page']}")

if st.session_state.selected_notice:
    notice = st.session_state.selected_notice
    
    # 목록으로 돌아가기 버튼
    back = st.button(
        label='⬅ 목록으로',
        type='secondary'
        )
    if back:
        st.session_state.selected_notice = None
        st.rerun()

    st.subheader(f"[{notice.get('date')}] {notice.get('title')}")
    st.divider()
    st.write(notice.get('content'))

else:
    st.subheader('공지사항')
    for notice in utils.utilsDb().notice:
        selectBTN = st.button(
            label=f"{notice.get('date')} | {notice.get('title')}",
            type='tertiary',
            width='content'
            )
        if selectBTN:
            st.session_state.selected_notice = notice
            st.rerun()