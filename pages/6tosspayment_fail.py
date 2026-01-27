import streamlit as st
import utils
import time
import streamlit.components.v1 as components

# iframe 탈출 코드 (결제 실패 시 redirection 문제 해결)
components.html(
    """
    <style>
        .container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #ffffff;
        }
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #e74c3c;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .message {
            color: #333;
            font-size: 16px;
            font-weight: 500;
        }
    </style>
    <div class="container">
        <div class="loader"></div>
        <div class="message">결제 결과를 확인 중입니다...</div>
    </div>
    <script>
        try {
            // 현재 창(window.self)이 최상위 창(window.top)과 다르면 iframe 내부에 있는 것입니다.
            if (window.self !== window.top) {
                // 현재 iframe의 URL(파라미터 포함)로 최상위 창을 이동시킵니다.
                window.top.location.href = window.location.href;
            }
        } catch (e) {
            console.error("Frame breakout failed", e);
        }
    </script>
    """,
    height=300
)

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO - 결제 실패',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)

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
st.switch_page("pages/5orderPage.py")
