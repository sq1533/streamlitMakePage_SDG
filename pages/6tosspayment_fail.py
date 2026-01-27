import streamlit as st
import utils
import time
import streamlit.components.v1 as components

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO - 결제 실패',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)

# iframe 탈출 코드 (결제 실패 시 redirection 문제 해결)



# 페이지 UI 변경 사항
utils.set_page_ui()
utils.init_session()

code = st.query_params.get("code")
message = st.query_params.get("message")

if code and message:
    st.error(f"결제가 실패했습니다.\n사유: {message} ({code})")
else:
    st.error("결제 중 오류가 발생했습니다.")

time.sleep(3)
st.markdown(
    f"""
    <meta http-equiv="refresh" content="0; url=https://amuredo.shop/orderPage">
    <script>
        window.top.location.href = "https://amuredo.shop/orderPage";
    </script>
    """,
    unsafe_allow_html=True
)