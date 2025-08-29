import streamlit as st
import time

# 인증 결과 페이지
if "email" not in st.query_params:
    st.query_params.email = False

if st.query_params:
    st.switch_page(page="mainPage.py")
else:
    st.success("인증이 완료되었습니다. 환영합니다.")
    time.sleep(2)
    st.switch_page(page="mainPage.py")