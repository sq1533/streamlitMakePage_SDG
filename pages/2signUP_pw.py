import streamlit as st
import userFunc.userAuth as userAuth
import re

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'firebase':None,
        'naver':None,
        'kakao':None,
        'gmail':None
    }

# 회원가입 진입
if 'signUP' not in st.session_state:
    st.session_state.signUP = False
# 회원가입 이메일
if 'email' not in st.session_state:
    st.session_state.email = None

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
if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')
else:
    if st.session_state.signUP and st.session_state.email:
        with st.sidebar:
            st.title(body='PASSWORD')

        empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

        with main.container():
            st.progress(
                value=33,
                text="비밀번호 설정"
            )

            PW = st.text_input(
                label="비밀번호",
                value=None,
                key="userPW",
                type="password",
                placeholder="08 ~ 20, 영문, 숫자, 특수문자 포함"
            )

            PWcheck = st.text_input(
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

            if PW:
                # 비밀번호 길이
                if 8 <= len(PW) <= 20:
                    access['length'] = 'green'
                else:
                    pass
            
                # 비밀번호 대소문자 영문
                if re.search(r'[a-zA-Z]', PW):
                    access['eng'] = 'green'
                else:
                    pass
            
                # 비밀번호 숫자
                if re.search(r'[0-9]', PW):
                    access['num'] = 'green'
                else:
                    pass
            
                # 비밀번호 특수문자
                if re.search(r"[!@#$%^&*(),.?:<>'/]", PW):
                    access['special'] = 'green'
                else:
                    pass
                
                # 비밀번호 재확인
                if PW == PWcheck:
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
                    label="사용자 정보 입력",
                    key="userInfo",
                    type="primary",
                    use_container_width=True,
                    disabled=False
                )
                if next:
                    createUser = userAuth.guest.createUser(email=st.session_state.email, pw=PW)
                    if createUser:
                        st.switch_page(page="pages/2signUP_userInfo.py")
                    else:
                        st.warning(body='가입 중 오류발생, 이메일과 비밀번호를 확인해주세요.')
    else:
        st.switch_page(page="mainPage.py")