import streamlit as st
import pandas as pd

import utils
from api import guest

class items(utils.database):

    # 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def showItem() -> pd.DataFrame:
        itemInfo : dict = utils.database().firestore_item
        keys = list(itemInfo.keys())
        items = []
        for key in keys:
            items.append(itemInfo.get(key).model_dump())

        itemData = pd.DataFrame(
            data=items,
            index=keys,
            columns=['series', 'color', 'event', 'category', 'name', 'price', 'discount', 'paths', 'detail', 'package', 'created_at']
            )
        return itemData

    # 상품 상태 일괄 조회
    def getAllItemStatus() -> dict:
        try:
            allStatus = utils.database().realtimeDB.reference(path='itemStatus').get()
            return allStatus if allStatus else {}
        except Exception as e:
            print(f"전체 상태 조회 실패: {e}")
            return {}

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus : dict = utils.database().realtimeDB.reference(path=f'itemStatus/{itemId}').get()
            return itemStatus
        except Exception as e:
            return {'failed' : str(e)}

    # 아이템 구매 및 상태 변경
    def itemOrder(token : dict, itemID : str, orderTime : str, address : str, comment : str|None, payToken : str, pay : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False
        
        uid = str(uid.get('result'))

        orderData = {
            'item' : itemID,
            'address' : address,
            'comment' : comment,
            'status' : 'ready',
            'payToken' : payToken,
            'pay' : pay
            }
        utils.database().realtimeDB.reference(path=f'user/{uid}/orderList/{orderTime}').set(orderData)
        utils.database().realtimeDB.reference(path=f'orderList/newOrder/{orderTime+'_'+uid}').set({'item':itemID})

        itemStatus : dict = utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').get()
        countResults = int(itemStatus.get('count')) - 1
        salesResults = int(itemStatus.get('sales')) + 1
        # 상품 구매 가능상태 > 재고 10개 이하 구분
        if countResults <= 10:
            itemResults = {
                'count' : countResults,
                'enable' : False,
                'sales' : salesResults
            }
            utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').update(itemResults)
            return True

        else:
            itemResults = {
                'count' : countResults,
                'sales' : salesResults
            }
            utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').update(itemResults)
            return True

    def addFeedback(token : dict, key : str, itemID : str, feedback : int, feedT : str|None) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.database().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'feedback':feedback})
        fb : dict = utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}/feedback').get()
        textReview : list = fb.get('text')
        textReview.append(key+'_'+feedT)
        result = {
            'point' : fb.get('point') + feedback,
            'count' : fb.get('count') + 1,
            'text' : textReview
        }
        utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}/feedback').update(result)
        return True

    # 주문상품 배송지 변경
    def orderAddrChange(token : dict, key : str, addr : str, comment : str|None) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        utils.database().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'address':addr, 'comment':comment})
        return True

    # 주문 취소 및 환불
    def orderCancel(token : dict, key : str, itemID : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        # 주문 취소 리스트 이동
        utils.database().realtimeDB.reference(path=f'orderList/cancel/{key+'_'+uid}').set({'item':itemID})
        utils.database().realtimeDB.reference(path=f'orderList/newOrder/{key+'_'+uid}').delete()

        # 상품 상태 변경
        itemStatus : dict = utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').get()
        countResults = int(itemStatus.get('count')) + 1
        salesResults = int(itemStatus.get('sales')) - 1
        if itemStatus.get('enable'):
            itemResults = {
                'count' : countResults,
                'sales' : salesResults
            }
        else:
            if countResults <= 10:
                itemResults = {
                    'count' : countResults,
                    'sales' : salesResults
                }
            else:
                itemResults = {
                    'count' : countResults,
                    'enable' : True,
                    'sales' : salesResults
                }
        itemStatus = utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').update(itemResults)

        # 고객 data 처리
        itemStatus = utils.database().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'status':'cancel'})
        return True

    # 환불 요청
    def orderRefund(token : dict, key : str, itemID : str) -> bool:
        uid : dict = guest.tokenToUid(token=token)
        if not uid.get('allow'):
            print('고객정보 호출 실패')
            return False

        uid = str(uid.get('result'))

        # 주문 환불 리스트 이동
        utils.database().realtimeDB.reference(path=f'orderList/delivery/{key+'_'+uid}').delete()
        utils.database().realtimeDB.reference(path=f'orderList/complete/{key+'_'+uid}').delete()
        utils.database().realtimeDB.reference(path=f'orderList/refund/{key+'_'+uid}').set({'item':itemID})

        # 환불된 상품 count 처리
        itemStatus : dict = utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').get()
        refundResults = int(itemStatus.get('refund')) + 1
        utils.database().realtimeDB.reference(path=f'itemStatus/{itemID}').update({'refund':refundResults})

        # 고객 data 처리
        utils.database().realtimeDB.reference(path=f'user/{uid}/orderList/{key}').update({'status':'refund'})
        return True