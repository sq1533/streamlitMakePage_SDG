# 자체 회원가입 일시정지
# import streamlit as st
# import userFunc.userAuth as userAuth
# from datetime import datetime, timezone, timedelta

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
# # 회원가입 이메일
# if 'email' not in st.session_state:
#     st.session_state.email = None

# # 고객 주소 정보
# if 'address' not in st.session_state:
#     st.session_state.address = '배송지 입력하기'

# st.html(
#     body="""
#     <style>
#     [data-testid="stHeaderActionElements"] {
#         display: none !important;
#     }
#     </style>
#     """
# )

# now = datetime.now(timezone.utc) + timedelta(hours=9)
# nowDay = now.strftime('%Y-%m-%d')

# @st.dialog(title='주소 검색', width='large')
# def addrDialog():
#     dialogAddr = st.text_input(
#         label="주소",
#         value=None,
#         key="addrTrue",
#         type="default",
#         disabled=False
#     )
#     if dialogAddr == None:
#         st.markdown(body="검색창에 찾을 주소를 입력해주세요.")
#     else:
#         findAddr = userAuth.seachAddress(dialogAddr)
#         if findAddr['allow']:
#             for i in findAddr['result']:
#                 addrNo, btn = st.columns(spec=[5,1], gap='small', vertical_alignment='center')

#                 addrNo.markdown(body=i)

#                 choice = btn.button(
#                     label="선택",
#                     key=i,
#                     type="primary",
#                     use_container_width=True
#                 )
#                 if choice:
#                     st.session_state.address = i
#                     st.rerun()
#         else:
#             st.markdown(body="검색 실패, 다시 시도해주세요.")

# # 세션 정보 검증 및 이메일 검증
# if any(value is not None for value in st.session_state.token.values()):
#     st.switch_page(page='mainPage.py')
# else:
#     if st.session_state.signUP:
#         with st.sidebar:
#             st.title(body='고객 정보 입력')

#         empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

#         with main.container():
#             st.progress(
#                 value=66,
#                 text="거의 다 왔어요~!"
#             )

#             name = st.text_input(
#                 label="이름",
#                 value=None,
#                 key="userName",
#                 type="default"
#             )

#             phone = st.text_input(
#                 label="전화번호",
#                 value=None,
#                 key="userPhone",
#                 type="default"
#             )

#             addr, searchAddr = st.columns(spec=[4,1], gap='small', vertical_alignment='center')

#             addr.text_input(
#                 label="기본 배송지",
#                 value=st.session_state.address,
#                 key="addrNone",
#                 type="default",
#                 disabled=True
#             )

#             searchAddrB = searchAddr.button(
#                 label="찾아보기",
#                 key="addressSearch",
#                 type="primary",
#                 use_container_width=False
#             )

#             if searchAddrB:
#                 addrDialog()

#             detailAddr = st.text_input(
#                 label="상세주소",
#                 value="",
#                 key="detailAddr",
#                 type="default"
#             )
        
#             address = st.session_state.address + ' ' + detailAddr

#             sendEmail = st.button(
#                 label="인증 메일 보내기",
#                 key="done",
#                 type="primary",
#                 use_container_width=True
#             )
#             if sendEmail:
#                 if name == None or phone == None or detailAddr == None or st.session_state.address == '배송지 입력하기':
#                     st.error(body="아직 완료되지 않았어요.")
#                 else:
#                     infomation = {
#                         'email':st.session_state.email,
#                         'name':name,
#                         'phoneNumber':phone,
#                         'address':{
#                             'home':address
#                             },
#                         'createPW':nowDay
#                     }
#                     addDB = userAuth.guest.userInfoAddDB(email=st.session_state.email, userInfo=infomation)
#                     if addDB:
#                         st.info(body="인증 메일을 보내는 중이에요.")
#                         sendResult = userAuth.guest.sendEmail(userMail=st.session_state.email)
#                         if sendResult:
#                             st.switch_page(page="pages/2signUP_results.py")
#                         else:
#                             st.warning(body="이메일 인증 실패")
#                     else:
#                         st.warning(body="입력하신 정보에 오류가 있어요. 확인해주세요")
#     else:
#         st.switch_page(page="mainPage.py")