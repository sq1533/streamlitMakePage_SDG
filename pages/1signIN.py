import streamlit as st
import userFunc.userAuth as userAuth

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
# 회원 정보
if 'uid' not in st.session_state:
    st.session_state.uid = None

# 회원가입 진입
if 'signUP' not in st.session_state:
    st.session_state.signUP = False

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

if st.session_state.user:
    st.switch_page(page='mainPage.py')
else:
    with st.sidebar:
        st.title(body='로그인/회원가입')

    empty, main, empty = st.columns(spec=[1,4,1], gap='small', vertical_alignment='top')

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
            st.switch_page(page='mainPage.py')
        
        # 고객 네이버 로그인 요청 상태
        if 'code' in st.query_params and st.query_params.code:
            userInfo = userAuth.guest.naverUser(code=st.query_params.code, state=st.query_params.state)
            if userInfo:
                signIN = userAuth.guest.naverSignIN(response=userInfo['response'])
                if signIN['allow']:
                    st.session_state.uid = signIN['uid']
                    st.session_state.user = signIN['result']
                    st.rerun()
                else:
                    st.write(signIN['result'])
            else:
                st.write('고객 네이버 로그인 실패')

        # 고객 비로그인 상태
        else:
            st.markdown(
                body=f"""
                <a href="{userAuth.guest.naverSignUP()}" target="_self" style="display: inline-block; padding: 10px 20px; background-color: #03C75A; color: white; text-align: center; text-decoration: none; border-radius: 5px;">
                    네이버 아이디로 로그인 (HTML)
                </a>
                """,
                unsafe_allow_html=True
                )

            signUP, signIN = st.columns(spec=2, gap='small', vertical_alignment='center')

            # firebese 이메일 회원가입
            signUPB = signUP.button(
                label='회원가입',
                key='firebaseSignUP',
                type='secondary',
                use_container_width=True
            )

            # firebase 이메일 로그인
            signINB = signIN.button(
                label='email로그인',
                key='firebaseSignIN',
                type='primary',
                use_container_width=True
            )

            if signUPB:
                st.session_state.signUP = True
                st.switch_page(page='pages/2signUP.py')

            if signINB:
                st.switch_page(page='pages/1signIN_firebase.py')