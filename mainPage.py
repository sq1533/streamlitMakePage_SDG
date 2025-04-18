import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="centered",
    initial_sidebar_state="expanded"
)

# json 연동은 cloud DB연동 전까지 사용
import json
with open(file="storage/data/products.json", mode="r", encoding="utf-8") as f:
    products = json.load(fp=f)
itemID = products["item"].keys()
itemCounts = list(itemID)


st.title(
    body="shop_demo"
)

st.logo(
    image=products["logo"]["src"],
    size="large",
    icon_image=products["logo"]["src"]
)

def productPage(key):
    st.write("test")
    st.image(
            image=products["item"][key]["src"],
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )

st.sidebar.write("test")
col_1, col_2, col_3 = st.columns(spec=3, gap="small", vertical_alignment="center")

# 상품 카드
for i in range(itemCounts.__len__()):
    if i%3 == 0:
        with col_1.container(height=250, border=True):
            st.image(
                image=products["item"][itemCounts[i]]["src"],
                caption=None,
                use_container_width=True,
                clamp=False,
                output_format="auto"
                )
            st.write(f"product_{i}")
            if st.button(label="구매", key=itemCounts[i]):
                st.query_params["item"] = itemCounts[i]
    elif i%3 == 1:
        with col_2.container(height=250, border=True, key=itemCounts[i]):
            st.image(
                image=products["item"][itemCounts[i]]["src"],
                caption=None,
                use_container_width=True,
                clamp=False,
                output_format="auto"
                )
    else:
        with col_3.container(height=250, border=True, key=itemCounts[i]):
            st.image(
                image=products["item"][itemCounts[i]]["src"],
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