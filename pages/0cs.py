import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
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

st.title("📞 1:1 고객 문의")
st.markdown("궁금한 점이 있으시면 언제든지 문의해주세요.")
with st.container(border=True):
    # 로그인한 사용자라면 정보 자동 채우기 (선택 사항)
    # user_info = st.session_state.get('user', {})
    
    with st.form(key='cs_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("성함", placeholder="홍길동")
        with col2:
            phone = st.text_input("연락처", placeholder="010-1234-5678")
            
        email = st.text_input("이메일", placeholder="contact@example.com")
        
        st.divider()
        
        title = st.text_input("문의 제목", placeholder="문의 제목을 입력해주세요.")
        content = st.text_area("문의 내용", height=200, placeholder="자세한 문의 내용을 적어주시면 신속하게 답변해드립니다.")
        
        submit_btn = st.form_submit_button("문의하기", type="primary", use_container_width=True)
        if submit_btn:
            if not (name and phone and email and title and content):
                st.warning("모든 항목을 입력해주세요.")
            else:
                with st.spinner("문의를 전송하고 있습니다..."):
                    if send_inquiry_email(name, phone, email, title, content):
                        st.success("문의가 성공적으로 접수되었습니다! 빠른 시일 내에 답변 드리겠습니다.")
                    else:
                        st.error("문의 접수에 실패했습니다. 잠시 후 다시 시도해주세요.")