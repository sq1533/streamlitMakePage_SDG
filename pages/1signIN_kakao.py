import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
st.html(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

import api
import requests

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

# 회원 소셜 로그인 상태
if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')

else:
    # 카카오 로그인 요청
    if 'code' in st.query_params and st.query_params.code:
        kakaoToken : dict = api.guest.kakaoToken(code=st.query_params.code)
        if kakaoToken.get('allow'):
            userInfo = requests.post(
                url='https://kapi.kakao.com/v2/user/me',
                headers={'Authorization' : f'Bearer {kakaoToken['result']['access_token']}'}
            )
            if userInfo.status_code == 200:
                signIN : dict = api.guest.kakaoUser(response=userInfo.json())
                if signIN.get('allow'):
                    st.session_state.token['kakao'] = kakaoToken['result']
                    st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)
                    st.rerun()
            else:
                st.warning(body='고객 정보 확인불가')
        else:
            st.warning('고객 카카오 로그인 실패')
    else:
        st.switch_page(page='1signIN.py')