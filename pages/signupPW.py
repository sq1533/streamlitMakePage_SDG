import streamlit as st
import time
import utils
import re

# 회원 가입 step 검증
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 가입 이메일 정보
if "signup_email" not in st.session_state:
    st.session_state.signup_email = False

# 가입 이메일 정보
if "password" not in st.session_state:
    st.session_state.password = False

# 회원 비밀번호 설정
if st.session_state.signup_step:
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
        length, eng, num, special, check = "gray", "gray", "gray", "gray", "gray"
        lengthC, engC, numC, specialC, checkC = False, False, False, False, False

        if pw:
            # 비밀번호 길이
            if 8 <= len(pw) <= 20:
                length = "green"
                lengthC = True
            else:
                length = "gray"
            
            # 비밀번호 대소문자 영문
            if re.search(r'[a-zA-Z]', pw):
                eng = "green"
                engC = True
            else:
                eng = "gray"
            
            # 비밀번호 숫자
            if re.search(r'[0-9]', pw):
                num = "green"
                numC = True
            else:
                num = "gray"
            
            # 비밀번호 특수문자
            if re.search(r"[!@#$%^&*(),.?:<>'/]", pw):
                special = "green"
                specialC = True
            else:
                special = "gray"
            
            # 비밀번호 재확인
            if pw == pwCheck:
                check = "green"
                checkC = True
            else:
                check = "gray"
        
        st.badge(
            label="비밀번호 08 ~ 20 자리",
            icon=None,
            color=length
        )
        st.badge(
            label="비밀번호 영문 포함",
            icon=None,
            color=eng
        )
        st.badge(
            label="비밀번호 숫자 포함",
            icon=None,
            color=num
        )
        st.badge(
            label="비밀번호 특수문자 포함  __?__ __!__ __@__ __#__ __$__ __%__ __^__ __&__ __*__ __,__ __.__ __:__ __<__ __>__ __/__",
            icon=None,
            color=special
        )
        st.badge(
            label="비밀번호 재입력 일치",
            icon=None,
            color=check
        )
        if lengthC and engC and numC and specialC and checkC:
            next = st.button(
                label="사용자 정보 입력",
                key="userInfo",
                type="primary",
                use_container_width=True,
                disabled=False
            )
            if next:
                try:
                    st.session_state.password = pw
                    st.switch_page(page="pages/signupUserInfo.py")
                except Exception:
                    st.error(body="비밀번호 설정 실패")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")