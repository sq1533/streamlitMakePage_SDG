import streamlit as st
import time

st.error("이메일 인증 실패")
time.sleep(2)
st.switch_page(page="mainPage.py")