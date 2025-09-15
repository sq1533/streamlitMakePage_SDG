import streamlit as st
from utils import database

class items(database):
    # 모든 아이템의 category 호출
    @st.cache_data(ttl=36000)
    def itemCategory():
        try:
            keys = []
            color = []
            series = []
            allItems = database().rtDatabase_item.get()
            for key, values in allItems.items():
                keys.append(key)
                color.append(values['color'])
                series.append(values['series'])
            colorResult = list(set(color))
            seriesResult = list(set(series))
            return {'allow':True, 'key':keys, 'color':colorResult, 'series':seriesResult}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':'컬러 및 시리즈 조회 실패'}

    # 특정 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def itemInfo(itemId : str) -> dict:
        itemIF = database().rtDatabase_item.child(itemId).get()
        return itemIF

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        itemStatus = database().rtDatabase_itemStatus.child(itemId).get()
        return itemStatus

    # 아이템 구매 및 상태 변경
    def itemOrder(uid : str, token : str, itemID : str, orderTime : str, address : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('orderList').child(orderTime).set(
                data={
                    'item':itemID,
                    'address' : address,
                    'status' : 'ready'
                    },
                token=token
            )
            database().pyrebase_db_orderList.child('newOrder').child(orderTime+'_'+uid).set(
                data={
                    'item':itemID
                    },
                token=token
            )
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get(token=token).val()
            countResults = int(itemStatus['count']) - 1
            salesResults = int(itemStatus['sales']) + 1
            if countResults < 10:
                itemResults = {
                    'count' : countResults,
                    'enable' : False,
                    'sales' : salesResults
                }
                database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults,token=token)
                return True
            else:
                itemResults = {
                    'count' : countResults,
                    'sales' : salesResults
                }
                database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults,token=token)
                return True
        except Exception as e:
            print(f'상품 주문 실패 {e}')
            return False

    # 배송지 변경
    def cgAddr(uid : str, token : str, key : str, addr : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('orderList').child(key).update(data={'address':addr}, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 주문 취소 및 환불
    def orderCancel(uid : str, token : str, key : str, itemID : str):
        try:
            # admin data 처리
            database().pyrebase_db_orderList.child('newOrder').child(key+'_'+uid).remove(token=token)
            database().pyrebase_db_orderList.child('cancel').child(key+'_'+uid).set(
                data={
                    'item':itemID
                    },
                token=token
            )

            # 상품 상태 변경
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get(token=token).val()
            countResults = int(itemStatus['count']) + 1
            salesResults = int(itemStatus['sales']) - 1
            if itemStatus['enable']:
                itemResults = {
                    'count' : countResults,
                    'sales' : salesResults
                }
            else:
                if countResults >= 10:
                    itemResults = {
                        'count' : countResults,
                        'enable' : True,
                        'sales' : salesResults
                    }
                else:
                    itemResults = {
                        'count' : countResults,
                        'sales' : salesResults
                    }
            database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults, token=token)

            # 고객 data 처리
            database().pyrebase_db_user.child(uid).child('orderList').child(key).update(data={'status':'cancel'}, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 환불 요청
    def orderRefund(uid : str, token : str, key : str, itemID : str) -> bool:
        try:
            # admin data 처리
            database().pyrebase_db_orderList.child('newOrder').child(key+'_'+uid).remove(token=token)
            database().pyrebase_db_orderList.child('refund').child(key+'_'+uid).set(
                data={
                    'item':itemID
                    },
                token=token
            )

            # 상품 상태 변경
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get(token=token).val()
            refundResults = int(itemStatus['refund']) + 1
            itemResults = {
                'refund' : refundResults
            }
            database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults, token=token)

            # 고객 data 처리
            database().pyrebase_db_user.child(uid).child('orderList').child(key).update(data={'status':'refund'}, token=token)
            return True
        except Exception as e:
            print(e)
            return False