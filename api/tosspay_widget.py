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
    # [중요] Iframe Sandbox 권한 부여를 위해 st.markdown 사용
    # allow-top-navigation: 이 권한이 있어야 Iframe 내부(Toss)에서 최상위 창(Streamlit)을 리다이렉트할 수 있음
    # srcdoc을 사용해야 same-origin 정책이 유지되어 리다이렉트가 가능함 (data: URI는 origin이 null이 되어 차단됨)
    # html.escape()를 쓰면 태그(<, >)까지 바뀌어 텍스트로 나오므로, 따옴표와 앰퍼샌드만 직접 치환함
    escaped_html = html_code.replace('&', '&amp;').replace('"', '&quot;')
    
    iframe_code = f"""
    <iframe 
        srcdoc="{escaped_html}" 
        width="100%" 
        height="800" 
        frameborder="0" 
        sandbox="allow-forms allow-modals allow-popups allow-scripts allow-same-origin allow-top-navigation"
    ></iframe>
    """
    
    return st.markdown(iframe_code, unsafe_allow_html=True)