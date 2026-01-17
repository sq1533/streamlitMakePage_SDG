import utils
import time
import logging

def cleanup_zombie_reservations(log_func=print):
    """
    만료된 '좀비' 예약을 정리하고 재고를 복구합니다.
    
    Args:
        log_func (callable): 로그를 출력할 함수 (예: print, st.write, logger.info). 기본값은 print.
    """
    reservations_ref = utils.utilsDb().realtimeDB.reference(path='reservations')
    reservations = reservations_ref.get()
    
    if not reservations:
        log_func("청소할 예약 데이터가 없습니다.")
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
            log_func(f"🛑 만료된 예약 발견: {res_id} (Item: {item_id})")

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
                    log_func(f" -> ✅ 재고 복구 완료")
                    reservations_ref.child(res_id).delete()
                    log_func(f" -> 🗑️ 예약 데이터 삭제 완료")
                    count += 1
                else:
                    log_func(f" -> ❌ 재고 복구 트랜잭션 실패")

            except Exception as e:
                log_func(f" -> ❌ 처리 중 오류 발생: {e}")

    log_func(f"청소 완료! 총 {count}개의 좀비 예약을 처리했습니다.")
