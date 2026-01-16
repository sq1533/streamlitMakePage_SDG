import streamlit as st
import utils
import api
import time

SECRET_KEY = st.secrets["cleanerKey"]["key"]
request_key = st.query_params.get("key", "")

if request_key != SECRET_KEY:
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

def cleanup_logic():
    reservations_ref = utils.utilsDb().realtimeDB.reference(path='reservations')

    reservations = reservations_ref.get()
    
    if not reservations:
        st.write("청소할 예약 데이터가 없습니다.")
        return

    now = int(time.time())
    count = 0

    for res_id, data in reservations.items():
        if not isinstance(data, dict):
            continue

        status = data.get('status')
        expires_at = data.get('expires_at', 0)
        item_id = data.get('item')

        if status == 'reserved' and expires_at < now:
            st.write(f"🛑 만료된 예약 발견: {res_id} (Item: {item_id})")

            try:
                item_ref = utils.utilsDb().realtimeDB.reference(path=f"itemStatus/{item_id}")
                
                def restore_transaction(current_data):
                    if current_data is None:
                        return None

                    current_data['count'] = int(current_data.get('count', 0)) + 1
                    current_data['sales'] = int(current_data.get('sales', 0)) - 1
                    if current_data['count'] > 5:
                        current_data['enable'] = True
                    return current_data

                result = item_ref.transaction(restore_transaction)

                if result:
                    st.write(f" -> ✅ 재고 복구 완료")
                    reservations_ref.child(res_id).delete()
                    st.write(f" -> 🗑️ 예약 데이터 삭제 완료")
                    count += 1
                else:
                    st.error(f" -> ❌ 재고 복구 트랜잭션 실패")

            except Exception as e:
                st.error(f" -> ❌ 처리 중 오류 발생: {e}")

    st.success(f"청소 완료! 총 {count}개의 좀비 예약을 처리했습니다.")

# 실행
cleanup_logic()