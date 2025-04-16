import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

st.title(
    body="shop_demo"
)

product_1, product_2, product_3 = st.columns(3, gap="small", border=True, vertical_alignment="center")
product_1.write("test")