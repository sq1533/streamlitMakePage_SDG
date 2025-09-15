import streamlit as st
import userFunc.userAuth as userAuth

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
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

# 세션 정보 검증 및 이메일 검증
if st.session_state.user:
    st.switch_page(page='mainPage.py')
else:
    if st.session_state.signUP:
        # 사이드바 내용
        with st.sidebar:
            st.title("고객 회원 가입")

        # 메인 페이지
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
                st.session_state.clear()
                st.switch_page(page='mainPage.py')

            st.progress(
                value=0,
                text="이메일 입력 입력"
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

            if email:
                # email 유효성 검사
                with st.spinner(text="이메일을 확인해볼게요", show_time=True):
                    userEmail = userAuth.guest.emailCK(id=email)
                    if userEmail['allow']:
                        checkEmail = st.button(
                            label="다음",
                            key="goMakePW",
                            type="primary",
                            use_container_width=True
                        )
                        if checkEmail:
                            st.session_state.email = email
                            st.switch_page(page="pages/2signUP_pw.py")
                    else:
                        st.error(body=userEmail['result'])
    else:
        st.switch_page(page="mainPage.py")