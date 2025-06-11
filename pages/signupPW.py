import streamlit as st
import time
from utils import auth
import re

# 세션 정의
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "uid" not in st.session_state:
    st.session_state.uid = None

# 사용자 정보 저장
if st.session_state.signup_step:

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        with st.sidebar:
            st.title("환영합니다.")
        st.progress(
            value=66,
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
        length, eng, num, special, check = "gray", "gray", "gray", "gray", "gray"
        lengthC, engC, numC, specialC, checkC = False, False, False, False, False
        if pw:
            if 8 <= len(pw) <= 20:
                length = "green"
                lengthC = True
            else:
                length = "gray"
            if re.search(r'[a-zA-Z]', pw):
                eng = "green"
                engC = True
            else:
                eng = "gray"
            if re.search(r'[0-9]', pw):
                num = "green"
                numC = True
            else:
                num = "gray"
            if re.search(r"[!@#$%^&*(),.?:<>'/]", pw):
                special = "green"
                specialC = True
            else:
                special = "gray"
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
                    auth.update_user(
                        uid=st.session_state.uid,
                        password=pw
                    )
                    st.switch_page(page="pages/signupUserInfo.py")
                except Exception:
                    st.error(body="비밀번호 설정 실패")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")