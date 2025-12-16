import streamlit as st
import requests
import base64
import json

#페이 서비스 연동
class pay:
    def __init__(self):
        self.naverpayKey = st.secrets['naverpay']
        self.kakaopayKey = st.secrets['kakaopay']
        self.tosspayKey = st.secrets['tosspay']['testKey']
    
    # 네이버페이
    def naverpay():
        pass
    
    # 카카오페이
    def kakaopay():
        pass
    
    def create_tosspay_auto(self, orderNo: str, itemName: str, amount: int, retCancelUrl: str, resultCallback: str):
        url = 'https://pay.toss.im/api/v2/payments'
        headers = {'Content-Type':'application/json'}
        payload = {
            'orderNo':orderNo,
            'amount':amount,
            'amountTaxFree':0,
            'productDesc':itemName,
            'apiKey':self.tosspayKey,
            'retUrl':'https://localhost:8080/orderPage',
            'retCancelUrl':'https://localhost:8080/orderPage',
            'autoExecute':False
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 0:
                return {
                    'access': True,
                    'payToken': res_json.get('payToken'),
                    'checkoutPage': res_json.get('checkoutPage')
                }
            else:
                return {'access': False, 'message': res_json.get('msg')}
        except Exception as e:
            return {'access': False, 'message': str(e)}

    # [2단계] 결제 승인 (필수)
    def confirm_tosspay(self, payToken: str, orderNo: str, amount: int):
        url = 'https://pay.toss.im/api/v2/execute'
        headers = {'Content-Type':'application/json'}
        payload = {
            'apiKey': self.tosspayKey,
            'payToken': payToken,
            'orderNo': orderNo,
            'amount': amount
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            res_json = response.json()
            
            if response.status_code == 200 and res_json.get('code') == 0:
                return {"success": True, "data": res_json}
            else:
                return {"success": False, "message": res_json.get('msg')}
        except Exception as e:
            return {"success": False, "message": str(e)}