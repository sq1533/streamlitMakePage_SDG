import streamlit as st
import requests
import base64

def handle_payment_callback(secret_key: str):
    """
    결제 성공/실패 리다이렉트 후 쿼리 파라미터를 처리합니다.
    
    Args:
        secret_key (str): 토스페이먼츠 시크릿 키
        
    Returns:
        dict: 결제 승인 결과 또는 실패 정보
    """
    
    # 쿼리 파라미터 확인 (Streamlit 버전에 따라 st.query_params 또는 st.experimental_get_query_params 사용)
    # 여기서는 최신 버전 기준 st.query_params 사용 (dict-like)
    params = st.query_params
    
    payment_key = params.get("paymentKey")
    order_id = params.get("orderId")
    amount = params.get("amount")
    
    # 실패 케이스 (code, message)
    error_code = params.get("code")
    error_msg = params.get("message")
    
    if error_code:
        return {
            "status": "fail",
            "code": error_code,
            "message": error_msg,
            "orderId": order_id
        }
        
    if payment_key and order_id and amount:
        # 결제 승인 API 호출
        url = "https://api.tosspayments.com/v1/payments/confirm"
        
        # Secret Key Base64 인코딩
        # "Basic " + base64(secret_key + ":")
        secret_key_str = f"{secret_key}:"
        encoded_key = base64.b64encode(secret_key_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "paymentKey": payment_key,
            "amount": int(amount),
            "orderId": order_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            res_json = response.json()
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "data": res_json
                }
            else:
                return {
                    "status": "error",
                    "code": res_json.get("code"),
                    "message": res_json.get("message"),
                    "data": res_json
                }
                
        except Exception as e:
            return {
                "status": "exception",
                "message": str(e)
            }
            
    return None
