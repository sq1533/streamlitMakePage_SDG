import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import requests

utils.init_session()

# 회원 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')

else:
    with st.spinner(text='안녕하세요, gmail 로그인 승인 요청중입니다. 잠시만 기다려주세요.', show_time=True):
        # 고객 gmail 로그인 요청 상태
        if 'code' in st.query_params and st.query_params.code:
            gmailToken : dict = api.guest.gmailToken(code=st.query_params.code)
            if gmailToken.get('allow'):
                userInfo = requests.get(
                    url='https://people.googleapis.com/v1/people/me',
                    params={'personFields': 'names,emailAddresses,birthdays,phoneNumbers'},
                    headers={'Authorization': f'Bearer {gmailToken["result"]["access_token"]}'}
                )
                if userInfo.status_code == 200:
                    signIN : dict = api.guest.gmailUser(response=userInfo.json())
                    if signIN.get('allow'):
                        st.session_state.token['gmail'] = gmailToken['result']['access_token']
                        st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                        st.rerun()
                else:
                    st.warning(body='로그인 실패, 고객 정보 확인불가')
            else:
                st.warning('고객 gmail 로그인 실패')
        else:
            st.switch_page(page='1signIN.py')