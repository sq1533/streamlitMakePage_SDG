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

# 홈으로 이동
goHome = st.button(
    label="홈으로 이동",
    key="goHome",
    type="primary",
    use_container_width=False,
    disabled=False
)
if goHome:
    st.switch_page(page="mainPage.py")

"""
# 비밀번호
solt = secrets.token_urlsafe(nbytes=16)
# 이메일 인증 커스텀 설정
auth.ActionCodeSettings(

)
"""

# 세션 정보 검증
if st.session_state.signup_step:
    if "signupStep" not in st.query_params:
        st.progress(
            value=0,
            text=["이메일 입력 입력"]
        )
        email = st.text_input(
            label="아이디",
            value=None,
            max_chars=40,
            key="createID",
            type="default",
            help=None,
            placeholder="id@email.com"
        )
        next = st.button(
            label="이메일 인증하기",
            key="nextStep0",
            type="primary",
            use_container_width=True,
            disabled=False
        )
        if next:
            try:
                if auth.get_user_by_email(email=email).email_verified == True:
                    st.error("이미 존재하는 이메일입니다.")
                elif auth.get_user_by_email(email=email).email_verified == False:
                    alreadyN = st.button(
                        label="인증 이어하기",
                        key="step0already",
                        type="primary",
                        use_container_width=True
                    )
                    st.warning(body="회원가입을 시도하셨군요!, 회원가입을 이어하시겠습니까?")
                    if alreadyN:
                        st.session_state.signup_email = email
                        st.query_params.signupStep = "emailAccess"
            except auth.UserNotFoundError:
                auth.create_user(
                    email=st.session_state.signup_email,
                    email_verified=False,
                    password=None,
                    display_name=None,
                    photo_url=None,
                    disabled=False,
                    )
                st.session_state.signup_email = email
                st.query_params.signupStep = "emailAccess"
    elif st.query_params.signupStep == "emailAccess":
        st.progress(
            value=25,
            text=["이메일 인증"]
        )
        st.write("이메일을 확인해 주세요.")
else:
    st.error("올바른 접근이 아닙니다.")