import streamlit as st
import streamlit.components.v1 as components
import utils

# 페이지 설정 (UI 요소 최소화)
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')

# 세션 유지
utils.init_session()

# URL 파라미터 확인
target = st.query_params.get("target")

# 리다이렉트 대상 결정
if target == "success":
    dest_path = "/tosspayment_success"
elif target == "fail":
    dest_path = "/tosspayment_fail"
else:
    dest_path = "/mainPage"

# Iframe Breakout & Redirect Script
# 현재 쿼리 파라미터(paymentKey, orderId 등)를 그대로 유지하면서
# 최상위 창(window.top)을 목적지로 이동시킵니다.
html_content = f"""
<!DOCTYPE html>
<html>
<body>
    <script>
        // 현재 페이지의 모든 쿼리 파라미터 가져오기
        const searchParams = window.location.search;
        
        // 목적지 경로 (Origin 포함)
        const destination = window.location.origin + "{dest_path}" + searchParams;
        
        // 최상위 창으로 이동 (Iframe 탈출)
        window.top.location.href = destination;
    </script>
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif;">
        <p>결제 결과를 확인 중입니다...</p>
    </div>
</body>
</html>
"""

components.html(html_content, height=300)