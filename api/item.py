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

    # 아이템 구매 및 상태 변경 (트랜잭션 적용)
    def itemOrder(token : dict, itemID : str, orderTime : str, address : str, comment : str|None, payToken : str, pay : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False
        
        uid = str(uid.get('result'))

        # 트랜잭션 함수 정의
        def order_transaction(current_data):
            if current_data is None:
                return None

            try:
                current_count = int(current_data.get('count', 0))
            except ValueError:
                return None
                
            if current_count > 0:
                current_data['count'] = current_count - 1
                current_data['sales'] = int(current_data.get('sales', 0)) + 1

                if current_data['count'] <= 10:
                     current_data['enable'] = False

                return current_data
            else:
                return None

        try:
            ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
            result = ref.transaction(order_transaction)

            if result is not None:
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
            else:
                print("재고 부족 또는 트랜잭션 실패")
                return False
                
        except Exception as e:
            import traceback
            print("=== 트랜잭션 오류 상세 로그 ===")
            print(f"에러 메시지: {e}")
            print(f"에러 타입: {type(e)}")
            print(f"에러 args: {e.args}")
            traceback.print_exc()
            print("=============================")
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

    # 주문 취소 및 환불 (트랜잭션 적용)
    def orderCancel(token : dict, key : str, itemID : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        # 트랜잭션 함수 정의
        def cancel_transaction(current_data):
            if current_data is None:
                return None

            current_count = int(current_data.get('count', 0)) + 1
            current_sales = int(current_data.get('sales', 0)) - 1
            
            current_data['count'] = current_count
            current_data['sales'] = current_sales

            if current_count > 10:
                current_data['enable'] = True

            return current_data

        try:
            ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
            result = ref.transaction(cancel_transaction)
            
            if result is not None:
                # 주문 취소 리스트 이동 및 고객 상태 업데이트
                utils.utilsDb().realtimeDB.reference(path=f"orderList/cancel/{key+'_'+uid}").set({'item':itemID})
                utils.utilsDb().realtimeDB.reference(path=f"orderList/newOrder/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'status':'cancel'})
                return True
            else:
                print("취소 트랜잭션 실패")
                return False

        except Exception as e:
            print(f"취소 트랜잭션 오류: {e}")
            return False

    # 환불 요청 (트랜잭션 적용)
    def orderRefund(token : dict, key : str, itemID : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        # 트랜잭션 함수 정의 (환불 카운트 증가)
        def refund_transaction(current_data):
            if current_data is None:
                return None
            
            current_refund = int(current_data.get('refund', 0)) + 1
            current_data['refund'] = current_refund
            return current_data

        try:
            ref = utils.utilsDb().realtimeDB.reference(path=f'itemStatus/{itemID}')
            result = ref.transaction(refund_transaction)
            
            if result is not None:
                # 주문 환불 리스트 이동
                utils.utilsDb().realtimeDB.reference(path=f"orderList/delivery/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/complete/{key+'_'+uid}").delete()
                utils.utilsDb().realtimeDB.reference(path=f"orderList/refund/{key+'_'+uid}").set({'item':itemID})
                
                # 고객 data 처리
                utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'status':'refund'})
                return True
            else:
                return False
        except Exception as e:
            print(f"환불 트랜잭션 오류: {e}")
            return False

    # 교환 요청
    def orderExchange(token : dict, key : str, itemID : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        # 주문 교환 리스트 이동
        utils.utilsDb().realtimeDB.reference(path=f"orderList/delivery/{key+'_'+uid}").delete()
        utils.utilsDb().realtimeDB.reference(path=f"orderList/complete/{key+'_'+uid}").delete()
        utils.utilsDb().realtimeDB.reference(path=f"orderList/exchange/{key+'_'+uid}").set({'item':itemID})

        # 고객 data 처리
        utils.utilsDb().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'status':'exchange'})
        return True