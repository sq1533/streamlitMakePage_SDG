import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

# 세션 관리
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user" not in st.session_state:
    st.session_state.user = None
if "item" not in st.session_state:
    st.session_state.item = None

# FireBase secret_keys
secretKeyPath = {
    "type" : st.secrets["firebaseKey"]["type"],
    "project_id" : st.secrets["firebaseKey"]["project_id"],
    "private_key_id" : st.secrets["firebaseKey"]["private_key_id"],
    "private_key" : st.secrets["firebaseKey"]["private_key"],
    "client_email" : st.secrets["firebaseKey"]["client_email"],
    "client_id" : st.secrets["firebaseKey"]["client_id"],
    "auth_uri" : st.secrets["firebaseKey"]["auth_uri"],
    "token_uri" : st.secrets["firebaseKey"]["token_uri"],
    "auth_provider_x509_cert_url" : st.secrets["firebaseKey"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url" : st.secrets["firebaseKey"]["client_x509_cert_url"],
    "universe_domain" : st.secrets["firebaseKey"]["universe_domain"]
    }

# Firebase 사용자 keys
firebaseWebConfig = {
    "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
    "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
    "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
    "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
    "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
    "appId" : st.secrets["firebaseWebConfig"]["appId"],
    "databaseURL" : None
    }

# Firebase 앱이 이미 초기화되었는지 확인
if not firebase_admin._apps:
    # FireBase 연결
    try:
        path = credentials.Certificate(cert=secretKeyPath)
        firebase_admin.initialize_app(credential=path)
        print("FireBase 앱 초기화 완료")
    except Exception as e:
        print(f"false : {e}")

# 사용자 auth 연결
firebase = pyrebase.initialize_app(firebaseWebConfig)
pyrebase_auth = firebase.auth()
# firestore 연결
db = firestore.client()
logoDB = db.collection('logo') # 로고 정보 가져오기
logo = logoDB.document('logo').get().to_dict()
itemsDB = db.collection('items') # items 컬렉션 연결
items = itemsDB.get() # items 하위 문서 가져오기

# 사용자 로그인
def signin(id,pw):
    userInfoDB = db.collection('userInfo')
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
        user_doc = userInfoDB.document(user["localId"]).get()
        if user_doc.exists:
            st.session_state.user = user_doc.to_dict()
            print(f"사용자 로그인 성공.")
            st.rerun()
        else:
            st.error("로그인에 성공했으나 Firestore에서 사용자 정보를 찾을 수 없습니다.")
            st.session_state.user = None
            st.session_state.userToken = None
    except Exception as e:
        print(f"로그인 실패: {e}")
        st.session_state.user = None
        st.error(body="로그인 실패,\n\n\n아이디 또는 비밀번호를 확인해주세요.")

# 사용자 로그아웃
def logout():
    st.session_state.user = None
    st.rerun()

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

st.title(body="shop_demo") # 페이지 제목
st.logo(image=logo.get("path"), size="large") # 페이지 로고

# siderbar 정의
with st.sidebar:
    if st.session_state.user == None:
        ID = st.text_input(
            label="이메일",
            value=None,
            key="textID",
            type="default",
            placeholder=None
        )
        PW = st.text_input(
            label="비밀번호",
            value=None,
            key="textPW",
            type="password",
            placeholder=None
        )
        login = st.button(
            label="log-IN",
            type="primary",
            use_container_width=True
        )
        signup = st.button(
            label="회원가입",
            type="secondary",
            use_container_width=True
        )
        if login:
            signin(ID,PW)
        if signup:
            st.session_state.signup_step = True
            st.switch_page(page="pages/signup.py")
    else:
        logoutB = st.button(
            label="log-OUT",
            type="primary",
            use_container_width=True
        )
        if logoutB:
            logout()
        st.write(f"환영합니다, {st.session_state.user["name"]} 고객님!")
        if st.session_state.user["like"] == []:
            st.write("좋아요한 상품이 없습니다.")
        else:
            for i in st.session_state.user["like"]:
                st.write(items.document(i).get().to_dict()["name"])

# 상품 구매 dialog
@st.dialog("shop_demo")
def itemInfo(item):
    # 아이템 이미지 리스트 노출
    st.image(
            image=item.get("path"),
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )
    # 상품 이름
    st.write(item.get("name"))
    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="center")
    price.write(item.get("price"))
    buyBTN = buy.button(
        label="구매하기",
        key="buyItem",
        type="primary",
        use_container_width=True
    )
    if buyBTN:
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if st.session_state.user == None:
            st.write("로그인 해주세요.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            st.session_state.item = item.get("id")
            st.switch_page(page="pages/orderPage.py")

# grid 설정
column_0, column_1, column_2, column_3, column_4 = st.columns(spec=5, gap="small", vertical_alignment="top")

# 첫 줄 card 배치
with column_0.container(height=400, border=True):
    item = items[0].to_dict()
    st.image(
        image=item.get("path"),
        caption=None,
        use_container_width=True,
        clamp=False,
        output_format="auto"
        )
    st.write(f"{item.get("name")}")
    viewBTN = st.button(
        label="상세보기",
        key=item.get("id"),
        type="primary",
        use_container_width=True
        )
    if viewBTN:
        itemInfo(item=item)

with column_1.container(height=100, border=True):
    st.write("빈 곳_1")

with column_1.container(height=400, border=True):
    item = items[1].to_dict()
    st.image(
        image=item.get("path"),
        caption=None,
        use_container_width=True,
        clamp=False,
        output_format="auto"
        )
    st.write(f"{item.get("name")}")
    viewBTN = st.button(
        label="상세보기",
        key=item.get("id"),
        type="primary",
        use_container_width=True
        )
    if viewBTN:
        itemInfo(item=item)

with column_2.container(height=400, border=True):
    st.write("items")

with column_3.container(height=100, border=True):
    st.write("빈 곳_2")

with column_3.container(height=400, border=True):
    st.write("items")

with column_4.container(height=400, border=True):
    st.write("items")

# items 행 설정
count = 5
for line in range(3):
    for i in column_0, column_1, column_2, column_3, column_4:
        with i.container(height=400, border=True):
            st.write(f"items{count}")
            count += 1