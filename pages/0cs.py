import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

# 페이지 시작
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
    st.session_state.page['page'] = 'mainPage.py'
    st.switch_page(page=f"{st.session_state.page['page']}")

st.title('📞 1:1 고객 문의')
st.markdown('궁금한 점이 있으시면 언제든지 문의해주세요.')
with st.container(border=True):
    title = st.text_input(
        label='문의 제목',
        placeholder='문의 제목을 입력해주세요.'
        )
    content = st.text_area(
        label='문의 내용',
        height=200,
        placeholder='자세한 문의 내용을 적어주시면 신속하게 답변해드립니다.'
        )

    csBTN = st.button(
        label='문의하기',
        type='secondary',
        width='stretch'
        )
    if csBTN:
        if not (title and content):
            st.warning(body='모든 항목을 입력해주세요.')
        else:
            with st.spinner(text='문의를 전송하고 있습니다...'):
                result : bool = api.guest.sendEmail(userInfo=st.session_state.user, title=title, content=content)
                if result:
                    st.toast('문의가 성공적으로 접수되었습니다! 빠른 시일 내에 답변 드리겠습니다.', icon="✅")
                    time.sleep(0.7)
                    st.session_state.page['page'] = 'mainPage.py'
                    st.switch_page(page=f"{st.session_state.page['page']}")
                else:
                    st.toast('문의 접수에 실패했습니다. 잠시 후 다시 시도해주세요.', icon="❌")
                    time.sleep(0.7)
                    st.session_state.page['page'] = 'mainPage.py'
                    st.switch_page(page=f"{st.session_state.page['page']}")