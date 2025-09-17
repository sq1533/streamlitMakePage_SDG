# 자체 회원가입 일시정지
# import streamlit as st
# import time

# # 회원 로그인 구분
# if 'token' not in st.session_state:
#     st.session_state.token = {
#         'firebase':None,
#         'naver':None,
#         'kakao':None,
#         'gmail':None
#     }

# # 회원가입 진입
# if 'signUP' not in st.session_state:
#     st.session_state.signUP = False

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

# # 세션 검증 및 이메일 검증
# if any(value is not None for value in st.session_state.token.values()):
#     st.switch_page(page='mainPage.py')
# else:
#     if st.session_state.signUP:
#         with st.sidebar:
#             st.title("환영합니다.")

#         empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

#         with main.container():
#             st.progress(
#                 value=100,
#                 text="회원 가입 완료"
#             )
#             st.markdown(body="회원가입이 완료되었습니다.\n\n원활한 이용을 위해 이메일 인증을 완료해 주세요.")
#             with st.spinner(text='메인 페이지 이동중', show_time=True):
#                 time.sleep(2)
#                 st.session_state.clear()
#                 st.rerun()
#     else:
#         st.switch_page(page="mainPage.py")