import streamlit as st
import requests
import base64
import json

#페이 서비스 연동
class pay:
    def __init__(self):
        self.naverpayKey = st.secrets['naverpay']['testKey']
        self.checkoutPage_url = st.secrets['naverpay']['checkoutPage_url']
        self.naverpayReturnUrl = st.secrets['naverpay']['returnUrl']

        self.kakaopayKey = st.secrets['kakaopay']

        # 토스페이 기본 정보
        self.tosspayKey = st.secrets['tosspay']['testKey']
        self.tosspayRetUrl = st.secrets['tosspay']['retUrl']
        self.tosspayRetCancelUrl = st.secrets['tosspay']['retCancelUrl']

    def naverpayToken(self, orderNo: str, itemName: str, amount: int) -> dict:
        url = 'https://dev-pay.paygate.naver.com/naverpay-partner/naverpay/payments/v2/reserve'

        headers = {
            'X-Naver-Client-Id': self.naverpayKey['clientId'],
            'X-Naver-Client-Secret': self.naverpayKey['clientSecret'],
            'Content-Type': 'application/json'
        }
        
        # 리다이렉트 될 URL
        returnUrl = f'{self.naverpayReturnUrl}?orderNo={orderNo}'
        
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
                    'checkoutPage_url': f'{self.checkoutPage_url}{reserveId}'
                }
            else:
                return {'access': False, 'message': res_json.get('message')}
        except Exception as e:
            return {'access': False, 'message': str(e)}

    # 네이버페이 결제 승인 (Approve)
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
            return {'access': False, 'message': str(e)}
    
    # 카카오페이
    def kakaopay():
        pass
    
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
            return {'access': False, 'message': str(e)}

    # [2단계] 결제 승인 (필수)
    def confirm_tosspay(self, payToken: str, orderNo: str) -> dict:
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
            return {'access': False, 'message': str(e)}
    
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