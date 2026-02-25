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

import time
from email_validator import validate_email, EmailNotValidError

# 페이지 시작
with st.sidebar:
    utils.set_sidebarLogo()
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

st.title('📫 1:1 고객 문의')
st.markdown('궁금한 점이 있으시면 언제든지 문의해주세요.')

with st.container(border=True):
    email_input = st.text_input(
        label='답장받을 이메일',
        placeholder='example@domain.com'
        )
    content = st.text_area(
        label='문의 내용',
        height=300,
        placeholder='자세한 문의 내용을 적어주시면 신속하게 답변해드립니다.'
        )

    
    agree = st.checkbox(
        label='답변 전송을 위한 이메일 수집 및 이용에 동의합니다.',
        value=False
        )

    csBTN = st.button(
        label='문의하기',
        type='secondary',
        width='stretch',
        disabled=not agree  # 체크하지 않으면 버튼 비활성화
        )
    if csBTN:
        try:
            valid = validate_email(email_input, check_deliverability=False)
            clean_email = valid.email

            if not content:
                st.warning(body='모든 항목을 입력해주세요.')
            else:
                with st.spinner(text='전송중입니다...'):
                    result : bool = utils.sendCS(
                        email=clean_email,
                        content=content
                    )

                    if result:
                        st.toast('문의가 성공적으로 접수되었습니다! 빠른 시일 내에 답변 드리겠습니다.', icon="✅")
                        time.sleep(0.7)
                        st.switch_page(page="mainPage.py")
                    else:
                        st.toast('문의 접수에 실패했습니다. 잠시 후 다시 시도해주세요.', icon="❌")
                        time.sleep(0.7)
                        st.switch_page(page="mainPage.py")

        except EmailNotValidError as e:
            print(e)
            st.error("올바른 이메일 형식이 아닙니다.")