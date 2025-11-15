import streamlit as st

import utils
from api import guest

class items(utils.database):

    # 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def showItem() -> dict:
        itemInfo : dict = utils.database().firestore_item
        return itemInfo

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus : dict = utils.database().realtimeDB.reference().child('itemStatus').child(itemId).get()
            return itemStatus
        except Exception as e:
            return {'failed' : str(e)}

    # 아이템 구매 및 상태 변경
    def itemOrder(token : dict, itemID : str, orderTime : str, address : str) -> bool:
        uid = guest.tokenToUid(token)
        if uid['allow']:
            print('고객정보 호출 실패')
            return False
        
        uid = uid['result']

        orderData = {
            'item' : itemID,
            'address' : address,
            'status' : 'ready'
            }
        utils.database().realtimeDB.reference().child(uid).child('orderList').child(orderTime).set(orderData)
        utils.database().realtimeDB.reference().child('orderList').child('newOrder').child(orderTime+'_'+uid['result']).set({'item':itemID})

        itemStatus : dict = utils.database().realtimeDB.reference().child('itemStatus').child(itemID).get()
        countResults = int(itemStatus['count']) - 1
        salesResults = int(itemStatus['sales']) + 1
        # 상품 구매 가능상태 > 재고 10개 이하 구분
        if countResults <= 10:
            itemResults = {
                'count' : countResults,
                'enable' : False,
                'sales' : salesResults
            }
            utils.database().realtimeDB.reference().child('itemStatus').child(itemID).update(itemResults)
            return True

        else:
            itemResults = {
                'count' : countResults,
                'sales' : salesResults
            }
            utils.database().realtimeDB.reference().child('itemStatus').child(itemID).update(itemResults)
            return True


    def addFeedback(token : dict, key : str, itemID : str, feedback : int, feedT : str|None) -> bool:
        uid = guest.tokenToUid(token)
        if uid['allow']:
            print('고객정보 호출 실패')
            return False

        uid = uid['result']

        utils.database().realtimeDB.reference().child(uid).child('orderList').child(key).update({'feedback':feedback})
        fb = utils.database().realtimeDB.reference().child('itemStatus').child(itemID).child('feedback').get()
        fb['text'][key] = feedT
        result = {
            'point' : fb.get('point') + feedback,
            'count' : fb.get('count') + 1,
            'text' : fb['text']
        }
        utils.database().realtimeDB.reference().child('itemStatus').child(itemID).child('feedback').update(result)
        return True

    # 주문상품 배송지 변경
    def orderAddrChange(token : dict, key : str, addr : str) -> bool:
        uid = guest.tokenToUid(token)
        if uid['allow']:
            print('고객정보 호출 실패')
            return False

        uid = uid['result']

        utils.database().realtimeDB.reference().child('user').child(uid).child('orderList').child(key).update({'address':addr})
        return True

    # 주문 취소 및 환불
    def orderCancel(token : dict, key : str, itemID : str) -> bool:
        uid = guest.tokenToUid(token)
        if uid['allow']:
            print('고객정보 호출 실패')
            return False

        uid = uid['result']

        # 주문 취소 리스트 이동
        utils.database().realtimeDB.reference().child('orderList').child('newOrder').child(key+'_'+uid).delete()
        utils.database().realtimeDB.reference().child('orderList').child('cancel').child(key+'_'+uid).set({'item':itemID})

        # 상품 상태 변경
        itemStatus = utils.database().realtimeDB.reference().child('itemStatus').child(itemID).get()
        countResults = int(itemStatus['count']) + 1
        salesResults = int(itemStatus['sales']) - 1
        if itemStatus['enable']:
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
        itemStatus = utils.database().realtimeDB.reference().child('itemStatus').child(itemID).update(itemResults)

        # 고객 data 처리
        itemStatus = utils.database().realtimeDB.reference().child('user').child(uid).child('orderList').child(key).update({'status':'cancel'})
        return True

    # 환불 요청
    def orderRefund(token : dict, key : str, itemID : str) -> bool:
        uid = guest.tokenToUid(token)
        if uid['allow']:
            print('고객정보 호출 실패')
            return False

        uid = uid['result']

        # 주문 환불 리스트 이동
        utils.database().realtimeDB.reference().child('orderList').child('delivery').child(key+'_'+uid).delete()
        utils.database().realtimeDB.reference().child('orderList').child('complete').child(key+'_'+uid).delete()
        utils.database().realtimeDB.reference().child('orderList').child('refund').child(key+'_'+uid['result']).set({'item':itemID})

        # 환불된 상품 count 처리
        itemStatus : dict = utils.database().realtimeDB.reference().child('itemStatus').child(itemID).get()
        refundResults = int(itemStatus['refund']) + 1
        itemResults = {
            'refund' : refundResults
        }
        utils.database().realtimeDB.reference().child('itemStatus').child(itemID).update(itemResults)

        # 고객 data 처리
        utils.database().realtimeDB.reference().child('user').child(uid).child('orderList').child(key).update({'status':'refund'})
        return True