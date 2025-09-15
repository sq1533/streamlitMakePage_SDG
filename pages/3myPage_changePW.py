import streamlit as st
import userFunc.userAuth as userAuth
from datetime import datetime, timezone, timedelta
import re

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'firebase':None,
        'naver':None,
        'kakao':None,
        'gmail':None
    }
# 회원 정보 세션
if 'user' not in st.session_state:
    st.session_state.user = None

st.html(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

# 사용자 정보 저장
if any(value is not None for value in st.session_state.token.values()):
    with st.sidebar:
        st.title("비밀번호 변경")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            key='goHOME',
            type='primary',
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")

        pw = st.text_input(
            label='비밀번호',
            value=None,
            key='userPW',
            type='password',
            placeholder="08 ~ 20, 영문, 숫자, 특수문자 포함"
        )
        pwCheck = st.text_input(
            label='비밀번호 확인',
            value=None,
            key='userPWcheck',
            type='password',
            placeholder="비밀번호와 동일하게 입력해주세요."
        )
        # 비밀번호 보안 규칙 준수 검증
        access = {
            'length':'gray',
            'eng':'gray',
            'num':'gray',
            'special':'gray',
            'check':'gray'
        }

        if pw:
            # 비밀번호 길이
            if 8 <= len(pw) <= 20:
                access['length'] = 'green'
            else:
                pass
            
            # 비밀번호 대소문자 영문
            if re.search(r'[a-zA-Z]', pw):
                access['eng'] = 'green'
            else:
                pass
            
            # 비밀번호 숫자
            if re.search(r'[0-9]', pw):
                access['num'] = 'green'
            else:
                pass
            
            # 비밀번호 특수문자
            if re.search(r"[!@#$%^&*(),.?:<>'/]", pw):
                access['special'] = 'green'
            else:
                pass
                
            # 비밀번호 재확인
            if pw == pwCheck:
                access['check'] = 'green'
            else:
                pass
        else:
            pass

        st.badge(
            label="비밀번호 08 ~ 20 자리",
            icon=None,
            color=access['length']
        )
        st.badge(
            label="비밀번호 영문 포함",
            icon=None,
            color=access['eng']
        )
        st.badge(
            label="비밀번호 숫자 포함",
            icon=None,
            color=access['num']
        )
        st.badge(
            label="비밀번호 특수문자 포함  __?__ __!__ __@__ __#__ __$__ __%__ __^__ __&__ __*__ __,__ __.__ __:__ __<__ __>__ __/__",
            icon=None,
            color=access['special']
        )
        st.badge(
            label="비밀번호 재입력 일치",
            icon=None,
            color=access['check']
        )

        # 비밀번호 검증
        if 'gray' in access.values():
            pass
        else:
            next = st.button(
                label='비밀번호 변경',
                key='changePW',
                type='primary',
                use_container_width=True,
                disabled=False
            )
            if next:
                now = datetime.now(timezone.utc) + timedelta(hours=9)
                nowDay = now.strftime('%Y-%m-%d')
                userAuth.guest.PWchange(token=st.session_state.token, newPW=pw, date=nowDay)
                st.session_state.clear()
                st.rerun()
else:
    st.switch_page(page="mainPage.py")