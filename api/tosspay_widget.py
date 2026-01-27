import streamlit as st


def render_payment_widget(client_key, customer_key, amount, order_id, order_name, customer_name, customer_email, success_url, fail_url):
    """
    Toss Payments Widget 렌더링 함수
    Success/Fail 시 window.top.location.href를 사용하여 최상위 창을 이동시킵니다.
    """
    # Python 변수를 JSON 문자열로 안전하게 변환
    import json
    js_client_key = json.dumps(client_key)
    js_customer_key = json.dumps(customer_key)
    js_amount = json.dumps(amount)
    js_order_id = json.dumps(order_id)
    js_order_name = json.dumps(order_name)
    js_customer_name = json.dumps(customer_name)
    js_customer_email = json.dumps(customer_email)
    js_success_url = json.dumps(success_url)
    js_fail_url = json.dumps(fail_url)

    # HTML 코드 생성 (이전과 동일)
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <script src="https://js.tosspayments.com/v1/payment-widget"></script>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
                display: flex; 
                flex-direction: column;
                align-items: center; 
                padding: 20px;
                background-color: transparent;
                margin: 0;
            }}
            .container {{ width: 100%; max-width: 600px; }}
            #payment-method {{ margin-bottom: 20px; }}
            #agreement {{ margin-bottom: 20px; }}
            #payment-button {{ 
                width: 100%; 
                padding: 15px; 
                background-color: #3182f6; 
                color: white; 
                border: none; 
                border-radius: 8px; 
                font-size: 16px; 
                font-weight: 600; 
                cursor: pointer; 
                transition: background-color 0.2s; 
            }}
            #payment-button:hover {{ background-color: #1b64da; }}
            #payment-button:disabled {{ background-color: #ccc; cursor: not-allowed; }}
        </style>
    </head>
    <body>
        <div class="container">
            <!-- 결제 수단 영역 -->
            <div id="payment-method"></div>
            <!-- 이용 약관 영역 -->
            <div id="agreement"></div>
            <!-- 결제하기 버튼 -->
            <button id="payment-button">결제하기</button>
        </div>

        <script>
            const clientKey = {js_client_key};
            const customerKey = {js_customer_key};
            const amount = {js_amount};
            const orderId = {js_order_id};
            const orderName = {js_order_name};
            const customerName = {js_customer_name};
            const customerEmail = {js_customer_email};
            let successUrl = {js_success_url};
            let failUrl = {js_fail_url};

            // URL이 이미 절대 경로로 전달되므로 추가 처리 불필요
            if (!successUrl.startsWith('http')) {{
                successUrl = window.location.origin + successUrl;
            }}
            if (!failUrl.startsWith('http')) {{
                failUrl = window.location.origin + failUrl;
            }}

            const paymentButton = document.getElementById('payment-button');

            try {{
                const paymentWidget = PaymentWidget(clientKey, customerKey);

                paymentWidget.renderPaymentMethods('#payment-method', {{ value: amount }});
                paymentWidget.renderAgreement('#agreement');

                paymentButton.addEventListener('click', function() {{
                    paymentButton.disabled = true;
                    paymentButton.innerText = "처리 중...";
                    
                    const timeoutId = setTimeout(function() {{
                        if (paymentButton.disabled) {{
                            paymentButton.disabled = false;
                            paymentButton.innerText = "결제하기 (시간 초과 - 다시 시도)";
                        }}
                    }}, 15000);

                    paymentWidget.requestPayment({{
                        orderId: orderId,
                        orderName: orderName,
                        successUrl: successUrl,
                        failUrl: failUrl,
                        customerEmail: customerEmail,
                        customerName: customerName
                    }}).then(function (data) {{
                        console.log(data);
                        clearTimeout(timeoutId);
                    }}).catch(function (error) {{
                        clearTimeout(timeoutId);
                        paymentButton.disabled = false;
                        paymentButton.innerText = "결제하기";

                        if (error.code === 'USER_CANCEL') {{
                            // 사용자 취소
                        }} else {{
                            alert("결제 오류: " + error.message + " (" + error.code + ")");
                        }}
                    }});
                }});
            }} catch (e) {{
                console.error(e);
                alert("초기화 오류: " + e.message);
            }}
        </script>
    </body>
    </html>
    """
    # [최종 방어선] Sandbox 활성화 + JS Injection (Iframe Property)
    # 1. Sandbox가 없으면 Cross-Origin 정책에 의해 Top Navigation이 차단됨 (Step 977 오류)
    # 2. Javascript URI 방식은 Sandbox 권한 상속에 문제가 있을 수 있음 (Step 948 오류)
    # 3. 따라서 '빈 Iframe' 생성 후 Sandbox 권한을 부여하고, 스크립트로 내용을 주입하는 방식이 가장 안전함.
    import base64
    b64_html = base64.b64encode(html_code.encode("utf-8")).decode("utf-8")
    frame_id = f"toss_widget_{order_id}"
    
    # 1. 빈 Iframe 생성 (Sandbox 필수 포함)
    iframe_tag = f"""
    <iframe 
        id="{frame_id}"
        width="100%" 
        height="1000" 
        frameborder="0" 
        sandbox="allow-forms allow-modals allow-popups allow-scripts allow-same-origin allow-top-navigation"
    ></iframe>
    """
    
    # 2. JS로 내용 주입 (Base64 Decode -> srcdoc 속성 할당)
    # 이 방식은 HTML 파싱 오류를 방지하고 Sandbox 권한을 온전히 사용함
    script_tag = f"""
    <script>
        (function() {{
            var iframe = document.getElementById("{frame_id}");
            if (iframe) {{
                try {{
                    iframe.srcdoc = atob("{b64_html}");
                }} catch(e) {{
                    console.error("Toss Widget injection error: ", e);
                }}
            }}
        }})();
    </script>
    """
    
    return st.markdown(iframe_tag + script_tag, unsafe_allow_html=True)