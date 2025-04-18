import streamlit as st
# json 연동은 cloud DB연동 전까지 사용
import json
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
if "item" not in st.query_params:
    st.query_params.item = None
if "user" not in st.session_state:
    st.session_state.user = None


# sidebar 설정
with st.sidebar:
    if st.session_state.user == None:
        st.button(
            label="log-IN",
            on_click=None,
            type="primary",
            use_container_width=True
        )


# MainPage
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
        count += 1
        if count >= itemCounts.__len__():
            break

def productPage(key):
    st.write("test")
    st.image(
            image=products["item"][key]["src"],
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )

if st.query_params.item == None:
    st.write("test")
else:
    st.Page(
        page=productPage(key=st.query_params.item),
        title=f"{products["item"][st.query_params.item]["name"]}"
        )