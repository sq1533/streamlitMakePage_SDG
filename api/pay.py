import streamlit as st
import requests
import base64
import json
import utils

#페이 서비스 연동
class pay:
    def __init__(self):
        # 네이버페이 기본 정보
        self.naverpayKey = st.secrets['naverpay']['key']
        self.checkoutPage_url = st.secrets['naverpay']['checkoutPage_url']
        self.naverpayReturnUrl = st.secrets['naverpay']['returnUrl']

        # 카카오페이 기본 정보
        kakaopayKey = st.secrets['kakaopay']['key']
        self.kakaopayCid = st.secrets['kakaopay']['cid']
        self.kakaopayReturnUrl = st.secrets['kakaopay']['returnUrl']
        self.kakaopayCancelUrl = st.secrets['kakaopay']['cancelUrl']
        self.kakaopayFailUrl = st.secrets['kakaopay']['failUrl']
        self.kakao_headers = {
            'Authorization': f"SECRET_KEY {kakaopayKey}",
            'Content-Type': 'application/json'
        }

        # 토스페이 기본 정보
        self.tosspayKey = st.secrets['tosspay']['key']
        self.tosspayRetUrl = st.secrets['tosspay']['retUrl']
        self.tosspayRetCancelUrl = st.secrets['tosspay']['retCancelUrl']

        # 토스페이먼츠 (PG) 기본 정보
        self.tosspaymentsSecretKey = st.secrets['tosspayments']['secret_key']

    # 네이버페이 토큰 발급(paymentId)
    def naverpayToken(self, orderNo: str, itemName: str, amount: int) -> dict:
        url = 'https://dev-pay.paygate.naver.com/naverpay-partner/naverpay/payments/v2/reserve'

        headers = {
            'X-Naver-Client-Id': self.naverpayKey['clientId'],
            'X-Naver-Client-Secret': self.naverpayKey['clientSecret'],
            'Content-Type': 'application/json'
        }
        
        # 리다이렉트 될 URL
        returnUrl = f"{self.naverpayReturnUrl}?orderNo={orderNo}"
        
        payload = {
            'merchantPayKey':orderNo,
            'productName':itemName,
            'productCount':1,
            'totalPayAmount':amount,
            'taxScopeAmount':amount,
            'taxExScopeAmount':0,
            'returnUrl':returnUrl
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 'Success':
                return {
                    'access': True,
                    'reserveId': res_json['body']['reserveId'], # 결제 예약 ID
                    'checkoutPage_url': f"{self.checkoutPage_url}{reserveId}"
                }
            else:
                return {'access': False, 'message': res_json.get('message')}
        except Exception as e:
            utils.get_logger().error(f"네이버페이 토큰 발급 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 네이버페이 결제 승인
    def approve_naverpay(self, paymentId: str) -> dict:
        url = 'https://dev-pay.paygate.naver.com/naverpay-partner/naverpay/payments/v2/apply/payment'
        
        headers = {
            'X-Naver-Client-Id': self.naverpayKey['clientId'],
            'X-Naver-Client-Secret': self.naverpayKey['clientSecret'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'paymentId': paymentId
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 'Success':
                return {'access': True, 'data': res_json['body']}
            else:
                return {'access': False, 'message': res_json.get('message')}
        except Exception as e:
            utils.get_logger().error(f"네이버페이 승인 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 네이버페이 환불
    def refund_naverpay():
        pass


    # 카카오페이 토큰
    def kakaopayToken(self, orderNo: str, itemName: str, amount: int) -> dict:
        url = 'https://open-api.kakaopay.com/online/v1/payment/ready'

        approval_url = f"{self.kakaopayReturnUrl}?orderNo={orderNo}"
        cancel_url = f"{self.kakaopayCancelUrl}?orderNo={orderNo}"
        fail_url = f"{self.kakaopayFailUrl}?orderNo={orderNo}"

        data = {
            'cid':self.kakaopayCid,
            'partner_order_id':orderNo,
            'partner_user_id':orderNo,
            'item_name':itemName,
            'quantity':1,
            'total_amount':amount,
            'tax_free_amount':0,
            'approval_url':approval_url,
            'cancel_url':cancel_url,
            'fail_url':fail_url,
        }

        try:
            response = requests.post(url, headers=self.kakao_headers, json=data)
            res_json = response.json()
            
            if response.status_code == 200:
                return {
                    'access': True,
                    'tid': res_json['tid'],
                    'checkoutPage': res_json['next_redirect_pc_url']
                }
            else:
                utils.get_logger().error(f"카카오페이 응답 오류 : {response.status_code} {res_json.get('msg')}")
                return {'access': False, 'message': res_json.get('msg')}
        except Exception as e:
            utils.get_logger().error(f"카카오페이 준비 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 카카오페이 결제 승인
    def approve_kakaopay(self, tid: str, pg_token: str, orderNo: str) -> dict:
        url = 'https://open-api.kakaopay.com/online/v1/payment/approve'
        
        data = {
            'cid':self.kakaopayCid,
            'tid':tid,
            'partner_order_id':orderNo,
            'partner_user_id':orderNo,
            'pg_token':pg_token
        }
        
        try:
            response = requests.post(url, headers=self.kakao_headers, json=data)
            res_json = response.json()
            
            if response.status_code == 200:
                 return {'access': True, 'data': res_json}
            else:
                 return {'access': False, 'message': res_json.get('msg', 'Approval Failed')}
        except Exception as e:
            utils.get_logger().error(f"카카오페이 승인 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 카카오페이 환불
    def refund_kakaopay(self, tid : str, amount : int, reason : str) -> bool:
        url = 'https://open-api.kakaopay.com/online/v1/payment/cancel'

        data = {
            'cid':self.kakaopayCid,
            'tid':tid,
            'cancel_amount':amount,
            'cancel_tax_free_amount':0,
            'payload':reason
        }
        
        try:
            response = requests.post(url, headers=self.kakao_headers, json=data)
            res_json = response.json()
            
            if response.status_code == 200:
                return True
            else:
                utils.get_logger().error(f"카카오페이 환불 실패: {res_json}")
                return False
        except Exception as e:
            utils.get_logger().error(f"카카오페이 환불 오류: {e}")
            return False

    # 토스페이 토큰발급(payToken)
    def tosspayToken(self, orderNo: str, itemName: str, amount: int) -> dict:
        url = 'https://pay.toss.im/api/v2/payments'
        headers = {'Content-Type':'application/json'}
        payload = {
            'orderNo':orderNo,
            'amount':amount,
            'amountTaxFree':0,
            'productDesc':itemName,
            'apiKey':self.tosspayKey,
            'retUrl':self.tosspayRetUrl,
            'retCancelUrl':self.tosspayRetCancelUrl,
            'autoExecute':False
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 0:
                return {
                    'access':True,
                    'payToken':res_json.get('payToken'),
                    'checkoutPage':res_json.get('checkoutPage')
                }
            else:
                return {'access':False, 'message':res_json.get('msg')}
        except Exception as e:
            utils.get_logger().error(f"토스페이 토큰 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 결제 승인
    def approve_tosspay(self, payToken: str, orderNo: str) -> dict:
        url = 'https://pay.toss.im/api/v2/execute'
        headers = {'Content-Type':'application/json'}
        payload = {
            'apiKey':self.tosspayKey,
            'payToken':payToken,
            'orderNo':orderNo
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 0:
                return {'access':True, 'data':res_json}
            else:
                return {'access':False, 'message':res_json.get('msg')}
        except Exception as e:
            utils.get_logger().error(f"토스페이 승인 오류: {e}")
            return {'access': False, 'message': str(e)}

    # 토스페이먼츠 (PG) 결제 승인
    def confirm_tosspayments(self, paymentKey: str, orderId: str, amount: int) -> dict:
        url = "https://api.tosspayments.com/v1/payments/confirm"
        
        # Secret Key Base64 인코딩
        secret_key_str = f"{self.tosspaymentsSecretKey}:"
        encoded_key = base64.b64encode(secret_key_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "paymentKey": paymentKey,
            "orderId": orderId,
            "amount": amount
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
            utils.get_logger().error(f"토스페이먼츠 승인 오류: {e}")
            return {
                "status": "exception",
                "message": str(e)
            }
    
    # 토스페이 결제 환불
    def refund_tosspay(self, payToken : str, refundNo : str, reason : str) -> bool:
        url = 'https://pay.toss.im/api/v2/refunds'
        params = {
            'apiKey':self.tosspayKey,
            'payToken':payToken,
            'refundNo':refundNo,
            'reason':reason
        }
        
        try:
            response = requests.post(url, json=params)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 0:
                return True
            else:
                print(res_json.get('msg'))
                return False
        except Exception as e:
            print(e)
            return False

    # 토스페이먼츠 (PG) Key-in 결제
    def tosspayments_keyin(self, payment_data: dict) -> dict:
        url = "https://api.tosspayments.com/v1/payments/key-in"
        
        # Secret Key Base64 인코딩
        secret_key_str = f"{self.tosspaymentsSecretKey}:"
        encoded_key = base64.b64encode(secret_key_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payment_data, timeout=30)
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
            utils.get_logger().error(f"토스페이먼츠 Key-in 결제 오류: {e}")
            return {
                "status": "exception",
                "message": str(e)
            }

    # 토스페이먼츠 (PG) 환불 (결제 취소)
    def refund_tosspayments(self, paymentKey: str, cancelReason: str) -> bool:
        url = f"https://api.tosspayments.com/v1/payments/{paymentKey}/cancel"
        
        # Secret Key Base64 인코딩
        secret_key_str = f"{self.tosspaymentsSecretKey}:"
        encoded_key = base64.b64encode(secret_key_str.encode("utf-8")).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {encoded_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "cancelReason": cancelReason
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            res_json = response.json()
            
            # 200 OK and status is usually 'CANCELED' or similar in response data, but API returns transaction object.
            # If status code is 200, it succeeded.
            if response.status_code == 200:
                return True
            else:
                utils.get_logger().error(f"토스페이먼츠 환불 실패: {res_json.get('message')} ({res_json.get('code')})")
                print(f"토스페이먼츠 환불 실패: {res_json}")
                return False
        except Exception as e:
            utils.get_logger().error(f"토스페이먼츠 환불 오류: {e}")
            return False