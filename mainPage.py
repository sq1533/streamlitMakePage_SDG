import os
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials
# json 연동은 cloud DB연동 전까지 사용
with open(file="storage/data/products.json", mode="r", encoding="utf-8") as f:
    products = json.load(fp=f)
itemID = products["item"].keys()
itemCounts = list(itemID)

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="centered",
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

# FireBase secret_keys
secretKeyPath = os.path.join(os.path.dirname(__file__),"storage","secrets","firebaseKey.json")
if not firebase_admin._apps:  # Firebase 앱이 이미 초기화되었는지 확인
    # FireBase 연결
    try:
        path = credentials.Certificate(cert=secretKeyPath)
        firebase_admin.initialize_app(credential=path)
        print("FireBase 앱 초기화 완료")
    except Exception as e:
        print(f"false : {e}")

# 페이지 제목
st.title(
    body="shop_demo"
)

# 페이지 로고
st.logo(
    image=products["logo"]["src"],
    size="large",
    icon_image=products["logo"]["src"]
)

# 쿼리, 및 세션 관리
if "user" not in st.session_state:
    st.session_state.user = None

# siderbar 정의
with st.sidebar:
    if st.session_state.user == None:
        ID = st.text_input(
            label="아이디",
            value=None,
            max_chars=40,
            key="textID",
            type="default",
            placeholder="id@email.com"
        )
        PW = st.text_input(
            label="비밀번호",
            value=None,
            max_chars=20,
            key="textPW",
            type="password",
            placeholder="********"
        )
        st.button(
            label="log-IN",
            on_click=None,
            type="primary",
            use_container_width=True
        )
        signup = st.button(label="회원가입", type="secondary", use_container_width=True)
        if signup:
            # 회원가입 초기 화면 로드
            st.session_state.signup_step = 0
            st.switch_page(page="pages/signup.py")
    else:
        st.button(
            label="log-OUT",
            on_click=None,
            type="primary",
            use_container_width=True
        )

# MainPage
# 상품 구매 dialog
@st.dialog("itemPage")
def itemInfo(item):
    # 아이템 이미지 리스트 노출
    st.image(
            image=products["item"][item]["src"],
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )
    # 상품 이름
    st.write(products["item"][item]["name"])
    # 상품 가격 및 구매 버튼
    price, buyBTN = st.columns(spec=2, gap="small", vertical_alignment="center")
    price.write(products["item"][item]["price"])
    if buyBTN.button(label="buy", key="buyItem"):
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if st.session_state.user == None:
            st.write("로그인 해주세요.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            st.session_state.buyItem = item

# grid 설정
cards_1 = st.columns(spec=3, gap="small", vertical_alignment="center")
cards_2 = st.columns(spec=3, gap="small", vertical_alignment="center")
cards_3 = st.columns(spec=3, gap="small", vertical_alignment="center")
cards_4 = st.columns(spec=3, gap="small", vertical_alignment="center")

count = 0

# 상품 카드
for i in cards_1+cards_2+cards_3+cards_4:
    with i.container(height=400, border=True):
        st.image(
            image=products["item"][itemCounts[count]]["src"],
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )
        st.write(f"product_{itemCounts[count]}")
        if st.button(label="구매", key=itemCounts[count]):
            st.query_params["item"] = itemCounts[count]
            itemInfo(item=itemCounts[count])
        count += 1
        if count >= itemCounts.__len__():
            break