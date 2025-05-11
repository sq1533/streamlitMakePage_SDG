import streamlit as st

# 인증 결과 페이지
if "email" not in st.query_params:
    st.query_params.email = False

if st.query_params:
    st.error("잘못된 접근입니다.")
else:
    st.success("인증이 완료되었습니다. 회원가입을 이어서 해주세요.")