import streamlit as st
import streamlit.components.v1 as components
import json

def render_payment_widget(
    client_key: str,
    customer_key: str,
    amount: int,
    order_id: str,
    order_name: str,
    customer_email: str,
    customer_name: str,
    success_url: str,
    fail_url: str,
    height: int = 600
):
    """
    토스페이먼츠 결제 위젯(V2)을 렌더링합니다.
    
    Args:
        client_key (str): 토스페이먼츠 클라이언트 키
        customer_key (str): 고객 식별 키 (비회원일 경우 랜덤 문자열 등)
        amount (int): 결제 금액
        order_id (str): 주문 ID (중복 불가)
        order_name (str): 주문명
        customer_email (str): 고객 이메일
        customer_name (str): 고객명
        success_url (str): 결제 성공 시 리다이렉트 URL (window.location.origin + /page...)
        fail_url (str): 결제 실패 시 리다이렉트 URL
        height (int): 컴포넌트 높이 (픽셀)
    """
    
    # HTML/JS 템플릿
    html_code = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="utf-8" />
        <script src="https://js.tosspayments.com/v2/standard"></script>
        <style>
            body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
            #payment-method {{ width: 100%; }}
            #agreement {{ width: 100%; }}
            .button-area {{ padding: 0 24px 24px 24px; text-align: center; }}
            #payment-button {{
                width: 100%;
                padding: 14px;
                background-color: #3182f6;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                font-weight: 600;
            }}
            #payment-button:hover {{ background-color: #1b64da; }}
        </style>
    </head>
    <body>
        <!-- 결제 UI -->
        <div id="payment-method"></div>
        <!-- 이용약관 UI -->
        <div id="agreement"></div>
        <!-- 결제하기 버튼 -->
        <div class="button-area">
            <button id="payment-button">결제하기</button>
        </div>

        <script>
            async function main() {{
                const clientKey = "{client_key}";
                const customerKey = "{customer_key}";
                const button = document.getElementById("payment-button");
                let widgets = null;

                // 결제하기 버튼 이벤트 핸들러
                button.addEventListener("click", async function () {{
                    if (!widgets) {{
                        alert("결제 위젯이 정상적으로 로드되지 않았습니다.");
                        return;
                    }}
                    
                    try {{
                        await widgets.requestPayment({{
                            orderId: "{order_id}",
                            orderName: "{order_name}",
                            successUrl: "{success_url}",
                            failUrl: "{fail_url}",
                            customerEmail: "{customer_email}",
                            customerName: "{customer_name}",
                            windowTarget: "self"  // iframe 내에서 리다이렉트 처리
                        }});
                    }} catch (err) {{
                        console.error(err);
                        if (err.code === "USER_CANCEL") {{
                            // 사용자 취소
                        }} else {{
                            alert("결제 요청 중 에러가 발생했습니다: " + err.message);
                        }}
                    }}
                }});
                
                try {{
                    const tossPayments = TossPayments(clientKey);
                    
                    widgets = tossPayments.widgets({{
                        customerKey: customerKey
                    }});

                    await widgets.setAmount({{
                        currency: "KRW",
                        value: {amount}
                    }});

                    await widgets.renderPaymentMethods({{
                        selector: "#payment-method",
                        variantKey: "DEFAULT" 
                    }});

                    await widgets.renderAgreement({{
                        selector: "#agreement",
                        variantKey: "AGREEMENT" 
                    }});

                }} catch (error) {{
                    console.error("Widget initialization failed:", error);
                    document.getElementById("payment-method").innerHTML = 
                        "<div style='padding: 20px; color: red; text-align: center;'>결제 위젯 초기화 실패<br><small>" + error.message + "</small></div>";
                }}
            }}
            
            main();
        </script>
    </body>
    </html>
    """
    
    components.html(html_code, height=height)