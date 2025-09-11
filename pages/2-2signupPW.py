import streamlit as st
import utils
import re

# 회원 가입 step 검증
if 'signup_step'not in st.session_state:
    st.session_state.signup_step = False
# 가입 이메일 정보
if 'signup_email' not in st.session_state:
    st.session_state.signup_email = None

st.markdown(
    body="""
    <style>
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 회원 비밀번호 설정
if st.session_state.signup_step and st.session_state.signup_email:
    with st.sidebar:
        st.title("환영합니다.")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        st.progress(
            value=33,
            text="비밀번호 설정"
        )
        pw = st.text_input(
            label="비밀번호",
            value=None,
            key="userPW",
            type="password",
            placeholder="08 ~ 20, 영문, 숫자, 특수문자 포함"
        )
        pwCheck = st.text_input(
            label="비밀번호 확인",
            value=None,
            key="userPWcheck",
            type="password",
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
                label="사용자 정보 입력",
                key="userInfo",
                type="primary",
                use_container_width=True,
                disabled=False
            )
            if next:
                signUpUser = utils.guest.userOverlapCK(id=st.session_state.signup_email, pw=pw)
                if signUpUser:
                    st.session_state.pw = pw
                    st.switch_page(page="pages/2-3signupUserInfo.py")
                else:
                    st.warning(body='가입 중 오류발생, 이메일과 비밀번호를 확인해주세요.')
else:
    st.switch_page(page="mainPage.py")