import streamlit as st
import pandas as pd

import utils
from api import guest

class items(utils.database):

    # 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def showItem() -> pd.DataFrame:
        itemInfo : dict = utils.utilsDb().firestore_item
        keys = list(itemInfo.keys())
        items = []
        for key in keys:
            items.append(itemInfo.get(key).model_dump())

        itemData = pd.DataFrame(
            data=items,
            index=keys,
            columns=['series', 'color', 'event', 'category', 'sort', 'name', 'price', 'discount', 'paths', 'detail', 'package', 'created_at']
            )
        return itemData

    # 상품 상태 일괄 조회
    def getAllItemStatus() -> dict:
        try:
            allStatus = utils.utilsDb().realtimeDB.reference(path='itemStatus').get()
            return allStatus if allStatus else {}
        except Exception as e:
            print(f"전체 상태 조회 실패: {e}")
            return {}

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus : dict = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemId}').get()
            return itemStatus
        except Exception as e:
            return {'failed' : str(e)}

    # 재고 예약 (결제 전 선점)
    def reserveItem(token: dict, itemID: str, orderTime: str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            return False

        uid = str(uid_res.get('result'))
        logger = utils.get_logger() # 로거 획득

        # 트랜잭션: 재고 차감 및 예약 설정
        def reserve_transaction(current_data):
            if current_data is None: return None

            current_count = int(current_data.get('count', 0))
            if current_count <= 10:
                return None

            current_data['count'] = current_count - 1
            current_data['sales'] = int(current_data.get('sales', 0)) + 1

            if current_data['count'] <= 10:
                current_data['enable'] = False
            return current_data

        try:
            ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
            result = ref.transaction(reserve_transaction)

            if result:
                utils.utilsDb().realtimeDB.reference(path=f'reservations/{orderTime}_{uid}').set({
                    'item': itemID,
                    'status': 'reserved',
                    'timestamp': {'.sv': 'timestamp'}
                })
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"예약 트랜잭션 오류 (User:{uid}, Item:{itemID}): {e}")
            return False

    # 예약 취소 (결제 실패/취소 시 재고 복구)
    def cancelReservation(token: dict, itemID: str, orderTime: str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            return False

        uid = str(uid_res.get('result'))

        def restore_transaction(current_data):
            if current_data is None:
                return None

            current_data['count'] = int(current_data.get('count', 0)) + 1
            current_data['sales'] = int(current_data.get('sales', 0)) - 1

            if current_data['count'] > 10:
                current_data['enable'] = True
            return current_data

        try:
            res_ref = utils.utilsDb().realtimeDB.reference(path=f'reservations/{orderTime}_{uid}')
            if res_ref.get() is None:
                return False 

            res_ref.delete()

            ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
            ref.transaction(restore_transaction)
            return True
        except Exception as e:
            utils.get_logger().error(f"예약 취소 오류 (User:{uid}, Item:{itemID}): {e}")
            return False

    # 아이템 주문 확정 (예약 -> 주문 완료)
    def itemOrder(token : dict, itemID : str, orderTime : str, address : str, comment : str|None, payToken : str, pay : str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            print('고객정보 호출 실패')
            return False
        
        uid = str(uid_res.get('result'))

        try:
            res_ref = utils.utilsDb().realtimeDB.reference(path=f'reservations/{orderTime}_{uid}')
            if res_ref.get() is None:
                print("예약 정보를 찾을 수 없음")
                return False

            res_ref.delete()

            orderData = {
                'item' : itemID,
                'address' : address,
                'comment' : comment,
                'status' : 'ready',
                'payToken' : payToken,
                'pay' : pay
            }
            utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{orderTime}').set(orderData)
            utils.utilsDb().realtimeDB.reference(path=f"orderList/newOrder/{orderTime+'_'+uid}").set({'item':itemID})
            return True

        except Exception as e:
            utils.get_logger().error(f"주문 확정 오류 (User:{uid}, Item:{itemID}): {e}")
            return False

    def addFeedback(token : dict, key : str, itemID : str, feedback : int, feedT : str|None) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'feedback':feedback})
        fb : dict = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}/feedback').get()
        textReview : list = fb.get('text')
        textReview.append(key+'_'+feedT)
        result = {
            'point' : fb.get('point') + feedback,
            'count' : fb.get('count') + 1,
            'text' : textReview
        }
        utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}/feedback').update(result)
        return True

    # 주문상품 배송지 변경
    def orderAddrChange(token : dict, key : str, addr : str, comment : str|None) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'address':addr, 'comment':comment})
        return True

    # [SECURE] 주문 취소 및 환불 (중복 취소 방지 적용)
    def orderCancel(token : dict, key : str, itemID : str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            return False

        uid = str(uid_res.get('result'))

        def cancel_txn(current_data):
            if current_data is None:
                return None

            if current_data.get('status') != 'ready':
                return None

            current_data['status'] = 'cancel'
            return current_data

        try:
            logger = utils.get_logger()
            # 유저 주문 정보 트랜잭션
            order_ref = utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}')
            order_result = order_ref.transaction(cancel_txn)

            if order_result is None:
                return False

            # 재고 복구 트랜잭션 (주문 취소 성공 시에만 실행)
            def restore_stock_txn(current_data):
                if current_data is None: return None
                
                current_data['count'] = int(current_data.get('count', 0)) + 1
                current_data['sales'] = int(current_data.get('sales', 0)) - 1
                
                if current_data['count'] > 10:
                    current_data['enable'] = True
                
                return current_data

            try:
                item_ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
                item_ref.transaction(restore_stock_txn)
            except Exception as e:
                # [CRITICAL] 주문은 취소됐으나 재고 복구 실패
                logger.critical(f"CRITICAL: 주문취소(User:{uid}, Order:{key}) 완료 후 재고({itemID}) 복구 실패. 수동 확인 필요. 에러: {e}")
                # 유저 입장에서는 취소가 성공한 것이므로 True 반환

            # 3. 리스트 관리 (실패해도 치명적이지 않음)
            try:
                utils.utilsDb().realtimeDB.reference(path=f"orderList/cancel/{key+'_'+uid}").set({'item': itemID})
                utils.utilsDb().realtimeDB.reference(path=f"orderList/newOrder/{key+'_'+uid}").delete()
            except Exception as e:
                logger.error(f"리스트 관리 실패 (주문취소 후처리): {e}")
            
            return True

        except Exception as e:
            logger.error(f"취소 트랜잭션 오류 (User:{uid}, Order:{key}): {e}")
            return False

    # [SECURE] 환불 요청 (중복 처리 방지)
    def orderRefund(token : dict, key : str, itemID : str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            return False

        uid = str(uid_res.get('result'))

        def refund_txn(current_data):
            if current_data is None:
                return None
            if current_data.get('status') not in ['delivery', 'complete']:
                return None

            current_data['status'] = 'refund'
            return current_data

        try:
            logger = utils.get_logger()
            order_ref = utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}')
            order_result = order_ref.transaction(refund_txn)

            if order_result is None:
                return False

            def refund_count_txn(current_data):
                if current_data is None:
                    return None

                current_data['refund'] = int(current_data.get('refund', 0)) + 1
                return current_data

            try:
                ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
                ref.transaction(refund_count_txn)
            except Exception as e:
                logger.critical(f"CRITICAL: 환불승인(User:{uid}, Order:{key}) 완료 후 재고({itemID}) 통계 업데이트 실패. 에러: {e}")

            try:
                utils.utilsDb().realtimeDB.reference(path=f"orderList/delivery/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/complete/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/refund/{key+'_'+uid}").set({'item':itemID})
            except Exception as e:
                logger.error(f"리스트 관리 실패 (환불 후처리): {e}")
            
            return True

        except Exception as e:
            logger.error(f"환불 트랜잭션 오류 (User:{uid}, Order:{key}): {e}")
            return False

    # [SECURE] 교환 요청 (중복 처리 방지)
    def orderExchange(token : dict, key : str, itemID : str) -> bool:
        uid_res = guest.tokenToUid(token=token)
        if not uid_res.get('allow'):
            return False

        uid = str(uid_res.get('result'))

        def exchange_txn(current_data):
            if current_data is None:
                return None
            if current_data.get('status') not in ['delivery', 'complete']:
                return None

            current_data['status'] = 'exchange'
            return current_data

        try:
            logger = utils.get_logger()
            order_ref = utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}')
            order_result = order_ref.transaction(exchange_txn)

            if order_result is None:
                return False

            try:
                utils.utilsDb().realtimeDB.reference(path=f"orderList/delivery/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/complete/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/exchange/{key+'_'+uid}").set({'item':itemID})
            except Exception as e:
                logger.error(f"리스트 관리 실패 (교환 요청 후처리): {e}")

            return True

        except Exception as e:
            logger.error(f"교환 요청 오류 (User:{uid}, Order:{key}): {e}")
            return False