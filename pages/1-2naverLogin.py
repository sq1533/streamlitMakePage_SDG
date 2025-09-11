import streamlit as st
import utils
import urllib.parse
import requests

if st.query_params.code:
    naverParams = {
        'grant_type':'authorization_code',
        'client_id':st.secrets['naver_api']['client_id'],
        'client_secret':st.secrets['naver_api']['client_sc'],
        'code':st.query_params.code,
        'state':st.query_params.code
    }
    encoded_params = urllib.parse.urlencode(naverParams)
    test = requests.post(url='https://nid.naver.com/oauth2.0/token',params=encoded_params).json()
    test2 = requests.post(url='https://openapi.naver.com/v1/nid/me', headers={'Authorization':f'Bearer {test['access_token']}'}).json()
    st.write(test2)
else:
    st.session_state.clear()
    st.switch_page(page='mainPage.py')