import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon="🇦🇲",
    layout="wide",
    initial_sidebar_state="auto"
)

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
        kakaoToken = userAuth.guest.kakaoToken(code=st.query_params.code)
        if kakaoToken['allow']:
            userInfo = requests.post(
                url='https://kapi.kakao.com/v2/user/me',
                headers={'Authorization' : f'Bearer {kakaoToken['result']['access_token']}'}
            )
            if userInfo.status_code == 200:
                signIN = userAuth.guest.kakaoUser(response=userInfo.json())
                if signIN['allow']:
                    st.session_state.token['kakao'] = kakaoToken['result']
                    st.rerun()
            else:
                st.warning(body='고객 정보 확인불가')
        else:
            st.warning('고객 카카오 로그인 실패')
    else:
        st.switch_page(page='1signIN.py')