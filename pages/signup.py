import streamlit as st

# sidebar Nav 기능 비활성화
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def nextStep():
    st.session_state.signup_step += 1
# 이전 step
def prevStep():
    st.session_state.signup_step -= 1
if "signup_step" not in st.session_state:
    st.error("올바른 접근이 아닙니다.")
else:
    st.progress(
        value=st.session_state.signup_step/4,
        text=None
    )
    if st.session_state.signup_step == 0:
        ID = st.text_input(
            label="아이디",
            value=None,
            max_chars=40,
            key="createID",
            type="default",
            help=None,
            placeholder="id@email.com"
        )
        next = st.button(label="이메일 인증", key="step0next", type="primary", use_container_width=True, disabled=False)
        if next:
            st.session_state.signup_email = ID
            st.session_state.signup_emailAccess = "111111"
            nextStep()
    elif st.session_state.signup_step == 1:
        st.text_input(
            label="아이디",
            value=st.session_state.signup_email,
            max_chars=40,
            key="createIDdisabled",
            type="default",
            help=None,
            disabled=True
        )
        accessCode = st.text_input(
            label="인증번호",
            value=None,
            max_chars=6,
            key="accessCode",
            type="default",
            help=None,
            placeholder="123456"
        )
        accessBTN = st.button(label="인증", key="accessEmail", type="primary", use_container_width=True)
        if accessBTN:
            if accessCode == st.session_state.signup_emailAccess:
                st.button(label="다음", key="step1next", type="primary", use_container_width=True, on_click=nextStep, disabled=False)
            else:
                st.button(label="다음", key="step1next", type="primary", use_container_width=True, disabled=True)
        else:
            st.button(label="다음", key="step1next", type="primary", use_container_width=True, disabled=True)
        st.button(label="이전", key="step1prev", type="primary", use_container_width=True, on_click=prevStep)
    elif st.session_state.signup_step == 2:
        st.write("비밀번호 설정")
        st.button(label="다음", key="step2next", type="primary", use_container_width=True, on_click=nextStep)
    # signup_step_4 기타 정보 입력 > fierbase 저장
    elif st.session_state.signup_step == 3:
        st.write("사용자 정보 입력")
        st.button(label="이전", key="step3prev", type="primary", use_container_width=True, on_click=prevStep)
        st.button(label="완료", key="step3next", type="primary", use_container_width=True, on_click=nextStep)
    # signup_step_5 회원가입 완료 > mainPage 이동
    elif st.session_state.signup_step == 4:
        st.write("welcome.")
    else:
        st.error("올바른 접근이 아닙니다.")