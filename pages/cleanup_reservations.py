import api.batch

# ... 기존 접근 권한 검사 로직 뒤에 실행 ...

access_granted = False
# 간단한 키 검사 (기존 로직 유지)
if request_key == SECRET_KEY:
    access_granted = True

if not access_granted:
    st.error("접근 권한이 없습니다.")
    st.stop()

st.markdown(
    body="""
    <style>
    header {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
    )

st.title("🧹 좀비 예약 청소 중...")

# 분리된 로직 실행 (로그 출력 함수로 st.write 전달)
api.batch.cleanup_zombie_reservations(log_func=st.write)