import streamlit as st
from firebase_admin import auth

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

# 다음 step
def nextStep():
    st.session_state.signup_step += 1
# 이전 step
def prevStep():
    st.session_state.signup_step -= 1

# 세션 정보 검증
if "signup_step" not in st.session_state:
    st.error("올바른 접근이 아닙니다.")
else:
    st.progress(
        value=st.session_state.signup_step/4,
        text=["이메일 입력", "이메일 인증", "비밀번호 설정", "사용자 정보 입력", "회원가입 완료"][st.session_state.signup_step]
    )
    # step_1 이메일 유효성 검사
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
        next = st.button(
            label="이메일 인증",
            key="step0next",
            type="primary",
            use_container_width=True,
            disabled=False
            )
        if next:
            try: # 이메일 활성화 여부 확인
                if auth.get_user_by_email(email=ID).email_verified == True:
                    st.error("이미 존재하는 이메일입니다.")
                elif auth.get_user_by_email(email=ID).email_verified == False:
                    st.session_state.signup_email = ID
                    nextStep()
            except auth.UserNotFoundError:
                st.session_state.signup_email = ID
                auth.create_user(
                    email=st.session_state.signup_email,
                    email_verified=False
                    )
                nextStep()
    # step_2 이메일 검증
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
        accessBTN = st.button(
            label="인증",
            key="accessEmail",
            type="primary",
            use_container_width=True
            )
        if accessBTN:
            auth.generate_email_verification_link(email=st.session_state.signup_email)
            next = st.button(
                label="다음",
                key="step1next",
                type="primary",
                use_container_width=True
                )
            if next:
                if auth.get_user_by_email(email=st.session_state.signup_email).email_verified == False:
                    st.error("이메일 인증이 완료되지 않았습니다.")
                elif auth.get_user_by_email(email=st.session_state.signup_email).email_verified == True:
                    nextStep()
        prev = st.button(
            label="이전",
            key="step1prev",
            type="primary",
            use_container_width=True
            )
        if prev:
            prevStep()
    # step_3 이메일 검증 후 비밀번호 설정
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