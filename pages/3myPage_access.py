# 자체 회원가입 일시정지
# import streamlit as st
# import userFunc.userAuth as userAuth
# import time

# # 회원 로그인 구분
# if 'token' not in st.session_state:
#     st.session_state.token = {
#         'firebase':None,
#         'naver':None,
#         'kakao':None,
#         'gmail':None
#     }

# # 회원 정보 세션
# if 'user' not in st.session_state:
#     st.session_state.user = None

# # 비밀번호 인증시도 횟수
# if 'allowCount' not in st.session_state:
#     st.session_state.allowCount = 0

# st.markdown(
#     body="""
#     <style>
#     [data-testid="stHeaderActionElements"] {
#         display: none !important;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )

# if any(value is not None for value in st.session_state.token.values()):
#     if st.session_state.token.get('firebase') != None:
#         with st.sidebar:
#             st.title(body="마이페이지")

#         empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

#         with main.container():
#             # 홈으로 이동
#             goHome = st.button(
#                 label='HOME',
#                 key='goHome',
#                 type='primary',
#                 use_container_width=False,
#                 disabled=False
#             )
#             if goHome:
#                 st.switch_page(page="mainPage.py")

#             st.markdown(body="한번 더 인증해 주세요!")

#             PW = st.text_input(
#                 label="비밀번호",
#                 value=None,
#                 key="myinfoAccessPW",
#                 type="password",
#                 placeholder=None
#             )

#             access = st.button(
#                     label='인증',
#                     key='access',
#                     type='primary',
#                     use_container_width=True
#             )

#             if access:
#                 accessUser = userAuth.guest.signIN(id=st.session_state.user.get('email'), pw=PW)
#                 if st.session_state.allowCount <= 7:
#                     if accessUser['allow']:
#                         st.switch_page(page='pages/3myPage.py')
#                     else:
#                         st.markdown(body=f"인증에 실패 했습니다. 인증 실패 {st.session_state.allowCount}회")
#                 else:
#                     st.markdown(body=f"인증을 다수 실패했습니다. 로그아웃 및 메인 페이지로 이동합니다.")
#                     time.sleep(2)
#                     st.session_state.clear()
#                     st.rerun()
#     else:
#         st.switch_page(page='pages/3myPage.py')
# else:
#     st.switch_page(page="mainPage.py")