import streamlit as st
import time
from utils import auth, db
import time
import re
import requests

# userInfo store 연결
userConn = db.collection('userInfo')

# 세션 정의
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "uid" not in st.session_state:
    st.session_state.uid = None
if "address" not in st.session_state:
    st.session_state.address = None

sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]

# 사용자 주소 검색 팝업, API 신청시 유효 url 입력 필요
@st.dialog("address")
def searchAddress(address):
    if re.search(r"[\]\[%;<>=]", address):
        st.error(body="특수문자는 포함할 수 없습니다.")
    elif any(i in address.upper() for i in sqlInjection):
        st.error(body="포함할 수 없는 단어가 존재합니다.")
    else:
        addressKey = {
            "confmKey" : st.secrets["address_search"]["keys"],
            "currentPage" : 1,
            "countPerPage" : 10,
            "keyword" : address,
            "resultType" : "json"
        }
        try:
            response = requests.post("https://business.juso.go.kr/addrlink/addrLinkApi.do", data=addressKey)
            if response.status_code == 200:
                addrLen = response.json()["results"]["juso"].__len__()
                if addrLen == 0:
                    st.error(body="검색 결과가 없습니다.")
                else:
                    for i in range(addrLen):
                        st.write(response.json()["results"]["juso"][i]["zipNo"])
                        st.write(response.json()["results"]["juso"][i]["roadAddr"])
                        moreAddr = st.text_input(
                            label="상세주소",
                            value=None,
                            key=f"moreAddr{i}",
                            type="default"
                        )
                        choise = st.button(
                            label="선택",
                            key=f"choise{i}"
                        )
                        if choise:
                            st.session_state.address = f"{response.json()['results']['juso'][i]['roadAddr']} {moreAddr}"
                            st.rerun()
        except Exception as e:
            st.error(f"주소 검색 중 오류 발생: {e}")

if st.session_state.signup_step:
    with st.sidebar:
        st.write("환영합니다.")
    st.progress(
        value=100,
        text="마지막 단계에요!"
    )
    name = st.text_input(
        label="이름",
        value=None,
        key="userName",
        type="default"
    )
    phone = st.text_input(
        label="전화번호",
        value=None,
        key="userPhone",
        type="default"
    )
    addr = st.text_input(
        label="기본 배송지 설정하기",
        value=None,
        key="searchAddr",
        type="default"
    )
    searchAddr = st.button(
        label="검색",
        key="addressSearch",
        type="primary",
        use_container_width=False
    )
    userAddr = st.write(st.session_state.address)
    signupDone = st.button(
        label="회원가입 완료",
        key="done",
        type="primary",
        use_container_width=True
    )
    if searchAddr:
        searchAddress(addr)
    if signupDone:
        if name == None or phone == None or st.session_state.address == None:
            st.error(body="아직 완료되지 않았어요.")
        else:
            try:
                auth.update_user(
                    uid=st.session_state.uid,
                    disabled=False
                )
                userInfo = {
                    "id" : st.session_state.uid,
                    "name" : name,
                    "phone" : phone,
                    "address" : [st.session_state.address],
                    "like" : []
                }
                userConn.document(st.session_state.uid).set(userInfo)
                st.info(body="회원가입이 완료되었습니다.")
                time.sleep(2)
                st.switch_page(page="mainPage.py")
            except Exception as e:
                st.error(body=f"회원가입 실패: {e}")
else:
    st.error("올바른 접근이 아닙니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")