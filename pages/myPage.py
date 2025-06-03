import streamlit as st
import time
import re
import requests
from utils import pyrebase_auth, userInfoDB
from mainPage import logout, items_data

if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user" not in st.session_state:
    st.session_state.user = None
user_doc = userInfoDB.document(st.session_state.user["id"]).get()
sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]

st.markdown(
    """
    <style>
    div[aria-label="dialog"][role="dialog"] {
        width: 80% !important;
        max-width: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 사용자 로그인
def myinfoPass(id,pw):
    try:
        pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
        return True
    except Exception:
        return False

# 주소지 삭제
def deleteAddress(address):
    st.session_state.user["address"].remove(address)
    user_doc.reference.update({"address": st.session_state.user["address"]})
    st.rerun()

# 마이페이지 dialog
@st.dialog("배송지 추가")
def addressPOP(address):
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
                            label="추가",
                            key=f"choise{i}"
                        )
                        if choise:
                            if f"{response.json()['results']['juso'][i]['roadAddr']} {moreAddr}" in st.session_state.user["address"]:
                                st.error(body="중복된 배송지 입니다.")
                            else:
                                st.session_state.user["address"].append(f"{response.json()['results']['juso'][i]['roadAddr']} {moreAddr}")
                                user_doc.reference.update({"address": st.session_state.user["address"]})
                                st.rerun()
        except Exception as e:
            st.error(f"주소 검색 중 오류 발생: {e}")

if not st.session_state.user:
    st.error("잘못된 접근 입니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")
else:
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

    with st.sidebar:
        st.title(body="마이페이지")

    email, passwardBTN = st.columns(spec=[2,1], gap="small", vertical_alignment="bottom")
    email.text_input(
        label="Email",
        value=st.session_state.user["email"],
        key="myinfoEmail",
        type="default",
        disabled=True
    )
    passwardBTN.button(
        label="비밀번호 변경",
        key="myinfoPWbtn",
        type="primary",
        use_container_width=True
    )
    st.text_input(
        label="이름",
        value=st.session_state.user["name"],
        key="myinfoName",
        type="default",
        disabled=True
    )
    st.text_input(
        label="휴대폰 번호",
        value=st.session_state.user["phone"],
        key="myinfoPhone",
        type="default",
        disabled=True
    )
    for address in st.session_state.user["address"]:
        addr, deleteB = st.columns(spec=[5,1], gap="small", vertical_alignment="center")
        addr.write(address)
        deleteBTN = deleteB.button(
            label="삭제",
            key=f"delete_{address}",
            type="primary",
            use_container_width=True
            )
        if deleteBTN:
            deleteAddress(address=address)
    addAddress = st.text_input(
        label="추가 주소지",
        key="myinfoAddAddress",
        type="default"
    )
    addAddressBTN = st.button(
        label="배송지 검색",
        key="myinfoAddress",
        type="primary",
        use_container_width=True
    )
    if addAddressBTN:
        addressPOP(addAddress)