import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
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

import api

utils.init_session()

# 로그인 상태 확인
if any(value is not None for value in st.session_state.token.values()):
    st.switch_page(page='mainPage.py')

else:
    with st.sidebar:
        st.title(body='로그인/회원가입')

    empty, main, empty = st.columns(spec=[1,4,1], gap='small', vertical_alignment='top')

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            type='primary',
            width='content',
            disabled=False
        )
        if goHome:
            st.switch_page(page='mainPage.py')

        # 네이버 로그인 버튼
        st.html(
            body=f"""
            <style>
            .login-container {{
                width: 100%;
                margin: 20px auto;
                display: flex;
                flex-direction: column; /* 아이템을 세로(열) 방향으로 배치 */
                gap: 12px; /* 버튼 사이의 간격 */
            }}

            .social-login-btn {{
                display: flex;
                width: 100%;
                height: 50px;
                align-items: center;
                justify-content: center;
                text-decoration: none;
                border-radius: 6px;
                font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', '맑은 고딕', Dotum, '돋움', sans-serif;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                box-sizing: border-box;
                position: relative;
                transition: opacity 0.2s;
            }}

            .naver-login {{
                background-color: #03C75A;
                color: white;
            }}
            .kakao-login {{
                background-color: #FEE500;
                color: rgba(0, 0, 0, 0.85);
            }}
            .gmail-login {{
                background-color: #FFFFFF;
                color: #444444;
                border: 1px solid #E0E0E0;
            }}

            .social-logo {{
                position: absolute;
                left: 16px;
                top: 50%;
                transform: translateY(-50%);
                width: 20px;
                height: 20px;
                background-size: contain;
                background-repeat: no-repeat;
            }}

            .naver-logo {{
                width: 20px;
                height: 20px;
            }}
            .kakao-logo {{
                width: 18px;
                height: 18px;
            }}
            .gmail-logo {{
                width: 18px;
                height: 18px;
            }}

            .naver-logo {{
            background-image: url("https://img.icons8.com/external-sbts2018-solid-sbts2018/58/external-netflix-basic-ui-elements-2.2-sbts2018-solid-sbts2018.png");
            }}
            .kakao-logo {{
                background-image: url("https://img.icons8.com/external-tal-revivo-color-tal-revivo/48/external-free-instant-messaging-app-for-cross-platform-devices-logo-color-tal-revivo.png");
            }}
            .gmail-logo {{
                background-image: url(https://img.icons8.com/fluency/48/gmail-new.png);
            }}
            </style>
            <div class="login-container">
                <a href="{api.guest.naverSignUP()}" class="social-login-btn naver-login" target="_self">
                    <span class="social-logo naver-logo"></span>
                    <span class="btn-text">네이버로 시작하기</span>
                </a>
                <a href="{api.guest.kakaoSignUP()}" class="social-login-btn kakao-login" target="_self">
                    <span class="social-logo kakao-logo"></span>
                    <span class="btn-text">카카오로 시작하기</span>
                </a>
                <a href="{api.guest.gmailSignUP()}" class="social-login-btn gmail-login" target="_self">
                    <span class="social-logo gmail-logo"></span>
                    <span class="btn-text">Gmail로 시작하기</span>
                </a>
            </div>
            """
            )