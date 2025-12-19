import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='collapsed'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

# 홈으로 이동
goHome = st.button(
    label='HOME',
    type='primary',
    width='content',
    disabled=False
)
if goHome:
    st.switch_page(page='mainPage.py')

st.title(body='이용약관')

# 이용약관 내용 출력
st.text(body=utils.utilsDb().condition)

st.divider()
st.html(body=utils.utilsDb().infoAdmin)