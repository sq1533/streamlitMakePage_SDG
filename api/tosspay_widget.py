import streamlit.components.v1 as components

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
            // JSON.parse로 안전하게 데이터 로드 (Python에서 json.dumps로 넘김)
            const clientKey = {js_client_key};
            const customerKey = {js_customer_key};
            const amount = {js_amount};
            const orderId = {js_order_id};
            const orderName = {js_order_name};
            const customerName = {js_customer_name};
            const customerEmail = {js_customer_email};
            let successUrl = {js_success_url};
            let failUrl = {js_fail_url};

            // URL 처리
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

                    // 디버깅: 결제 시도 알림 (필요시 주석 처리)
                    // alert("결제 요청 시작: " + successUrl);

                    paymentWidget.requestPayment({{
                        orderId: orderId,
                        orderName: orderName,
                        successUrl: successUrl,
                        failUrl: failUrl,
                        customerEmail: customerEmail,
                        customerName: customerName
                    }}).catch(function (error) {{
                        paymentButton.disabled = false;
                        paymentButton.innerText = "결제하기";

                        if (error.code === 'USER_CANCEL') {{
                            // 사용자 취소 - 조용히 넘어감
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
    # 높이를 충분히 주어 스크롤이 생기지 않도록 함
    return components.html(html_code, height=800, scrolling=True)
