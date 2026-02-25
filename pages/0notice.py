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

# 공지 상세보기 세션 구분
if 'selected_notice' not in st.session_state:
    st.session_state.selected_notice = None

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

# 홈으로 이동
goHome = st.button(
    label='HOME',
    type='secondary',
    width='content',
    disabled=False
)
if goHome:
    st.switch_page(page='mainPage.py')

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