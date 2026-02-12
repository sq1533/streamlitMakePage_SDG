import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import requests
import urllib.parse
import base64

# 페이지 접근 확인
if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')

# 페이지 시작
with st.spinner(text='안녕하세요, 네이버 로그인 승인 요청중입니다. 잠시만 기다려주세요.', show_time=True):
    # 고객 네이버 로그인 요청 상태
    if 'code' in st.query_params and st.query_params.code:
        state_param = st.query_params.get('state', '')
        
        if '|' in state_param:
            try:
                # URL 디코딩 추가 (혹시 모를 이중 인코딩 대비)
                encoded_query = state_param.split('|')[1]
                # Base64 디코딩
                query_str = base64.urlsafe_b64decode(encoded_query).decode()
                restored_items = urllib.parse.parse_qsl(query_str)
                
                for key, value in restored_items:
                    st.session_state.page[key] = value
            except Exception as e:
                pass

        naverToken : dict = api.guest.naverToken(code=st.query_params.code, state=state_param)
        if naverToken.get('allow'):
            userInfo = requests.post(
                url='https://openapi.naver.com/v1/nid/me',
                headers={'Authorization':f"Bearer {naverToken['result']['access_token']}"}
                )
            if userInfo.status_code == 200 and userInfo.json()['resultcode'] == '00':
                signIN : dict = api.guest.naverUser(response=userInfo.json()['response'])
                if signIN.get('allow'):
                    st.session_state.token['naver'] = naverToken['result']['access_token']
                    st.session_state.user = api.guest.showUserInfo(token=st.session_state.token)['result']
                    st.switch_page(page=f"{st.session_state.page['page']}")
            else:
                st.warning(body='로그인 실패, 고객 정보 확인불가')
        else:
            st.warning('고객 네이버 로그인 실패')
    else:
        st.switch_page(page='1signIN.py')