import streamlit as st
import userFunc.userAuth as userAuth
import requests

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }

st.html(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')
else:
    # 고객 네이버 로그인 요청 상태
    if 'code' in st.query_params and st.query_params.code:
        naverToken = userAuth.guest.naverToken(code=st.query_params.code, state=st.query_params.state)
        if naverToken['allow']:
            userInfo = requests.post(
                url='https://openapi.naver.com/v1/nid/me',
                headers={'Authorization':f'Bearer {naverToken['result']['access_token']}'}
                )
            if userInfo.status_code == 200 and userInfo.json()['resultcode'] == '00':
                signIN = userAuth.guest.naverUser(response=userInfo.json()['response'])
                if signIN['allow']:
                    st.session_state.token['naver'] = naverToken['result']
                    st.rerun()
            else:
                st.warning(body='로그인 실패, 고객 정보 확인불가')
        else:
            st.warning('고객 네이버 로그인 실패')
    else:
        st.switch_page(page='1signIN.py')