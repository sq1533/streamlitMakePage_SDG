import streamlit as st
import utils

# state 세션 검증
if 'naverState' not in st.session_state:
    st.session_state.naverState = None

if st.query_params.state == st.session_state.naverState:
    st.info(body='state 일치')
else:
    st.warning(body='state 불일치')