import streamlit as st
from utils import database
import userFunc.userAuth as userAuth

class items(database):
    # 모든 아이템의 category 호출
    @st.cache_data(ttl=36000)
    def itemCategory():
        try:
            keys = []
            color = []
            series = []
            allItems = database().firestore_item
            for item in allItems:
                keys.append(item.id)
                item = item.to_dict()
                color.append(item['color'])
                series.append(item['series'])
            colorResult = list(set(color))
            seriesResult = list(set(series))
            return {'allow':True, 'key':keys, 'color':colorResult, 'series':seriesResult}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':'컬러 및 시리즈 조회 실패'}

    # 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def itemInfo() -> dict:
        itemIF = {}
        for i in database().firestore_item:
            itemIF[i.id] = i.to_dict()
        return itemIF

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        itemStatus = database().rtDatabase_itemStatus.child(itemId).get()
        return itemStatus

    # 아이템 구매 및 상태 변경
    def itemOrder(token : dict, itemID : str, orderTime : str, address : str) -> bool:
        uid = userAuth.guest.tokenToUid(token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child('orderList').child(orderTime).set(
                {
                'item':itemID,
                'address' : address,
                'status' : 'ready'
                }
            )
            database().rtDatabase_orderList.child('newOrder').child(orderTime+'_'+uid['result']).set({'item':itemID})

            itemStatus = database().rtDatabase_itemStatus.child(itemID).get()
            countResults = int(itemStatus['count']) - 1
            salesResults = int(itemStatus['sales']) + 1
            if countResults <= 10:
                itemResults = {
                    'count' : countResults,
                    'enable' : False,
                    'sales' : salesResults
                }
                database().rtDatabase_itemStatus.child(itemID).update(itemResults)
                return True
            else:
                itemResults = {
                    'count' : countResults,
                    'sales' : salesResults
                }
                database().rtDatabase_itemStatus.child(itemID).update(itemResults)
                return True
        else:
            print('고객정보 호출 실패')
            return False

    def addFeedback(token : dict, key : str, itemID : str, feedback : int):
        uid = userAuth.guest.tokenToUid(token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child('orderList').child(key).update({'feedback':feedback})
            fb = database().rtDatabase_itemStatus.child(itemID).child('feedback').get()
            result = {
                'point' : fb.get('point') + feedback,
                'count' : fb.get('count') + 1
            }
            database().rtDatabase_itemStatus.child(itemID).child('feedback').update(result)
            return True
        else:
            print('고객정보 호출 실패')
            return False

    # 배송지 변경
    def cgAddr(token : dict, key : str, addr : str) -> bool:
        uid = userAuth.guest.tokenToUid(token)
        if uid['allow']:
            database().rtDatabase_user.child(uid['result']).child('orderList').child(key).update({'address':addr})
            return True
        else:
            print('고객정보 호출 실패')
            return False

    # 주문 취소 및 환불
    def orderCancel(token : dict, key : str, itemID : str) -> bool:
        uid = userAuth.guest.tokenToUid(token)
        if uid['allow']:
            database().rtDatabase_orderList.child('newOrder').child(key+'_'+uid['result']).delete()
            database().rtDatabase_orderList.child('cancel').child(key+'_'+uid['result']).set({'item':itemID})

            # 상품 상태 변경
            itemStatus = database().rtDatabase_itemStatus.child(itemID).get()
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
            database().rtDatabase_itemStatus.child(itemID).update(itemResults)

            # 고객 data 처리
            database().rtDatabase_user.child(uid['result']).child('orderList').child(key).update({'status':'cancel'})
            return True
        else:
            print('취소 실패')
            return False

    # 환불 요청
    def orderRefund(token : dict, key : str, itemID : str) -> bool:
        uid = userAuth.guest.tokenToUid(token)
        if uid['allow']:
            database().rtDatabase_orderList.child('delivery').child(key+'_'+uid['result']).delete()
            database().rtDatabase_orderList.child('complete').child(key+'_'+uid['result']).delete()
            database().rtDatabase_orderList.child('refund').child(key+'_'+uid['result']).set({'item':itemID})

            # 상품 상태 변경
            itemStatus = database().rtDatabase_itemStatus.child(itemID).get()
            refundResults = int(itemStatus['refund']) + 1
            itemResults = {
                'refund' : refundResults
            }
            database().rtDatabase_itemStatus.child(itemID).update(itemResults)

            # 고객 data 처리
            database().rtDatabase_user.child(uid['result']).child('orderList').child(key).update({'status':'refund'})
            return True
        else:
            print('고객 환불 요청 실패')
            return False