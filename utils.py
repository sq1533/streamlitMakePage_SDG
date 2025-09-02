import streamlit as st
import pyrebase
from email_validator import validate_email, EmailNotValidError
import re
import json
import requests
from requests.exceptions import HTTPError

# Firebase 사용자 keys
firebaseWebConfig = {
    "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
    "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
    "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
    "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
    "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
    "appId" : st.secrets["firebaseWebConfig"]["appId"],
    "databaseURL" : st.secrets["firebaseWebConfig"]["databaseURL"]
    }

# pyrebase - firebase 연결
firebase = pyrebase.initialize_app(config=firebaseWebConfig)

# database
class database:
    def __init__(self):
        self.pyrebase_auth = firebase.auth() # 회원 인증
        self.pyrebase_db_user = firebase.database().child('user') # 회원 정보 db
        self.pyrebase_db_items = firebase.database().child('items') # items 정보 db
        self.pyrebase_db_itemStatus = firebase.database().child('itemStatus') # itemStatus 정보 db
        self.pyrebase_db_orderList = firebase.database().child('orderList') # orderList 정보 db
        self.showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료',
                'cancel':'취소 완료',
                'refund':'환불 요청 완료',
                'refunded':'환불 완료'
            }


# guest 관리
class guest(database):
    # 이메일 유효성 검사
    def emailCK(id : str) -> dict:
        try:
            if validate_email(id, check_deliverability=True, timeout=5)['email'] == id:
                return {'allow' : True, 'result' : id}
            else:
                return {'allow' : False, 'result' : '이메일 형식이 잘못되었습니다.'}
        except EmailNotValidError as emailError:
            return {'allow' : False, 'result' : f'이메일 검증 오류 {emailError}'}
        except Exception as e:
            print(e)
            return {'allow' : False, 'result' : f'예기치 못한 오류 {e}'}

    # 중복 회원 검증
    def userOverlapCK(id : str, pw : str) -> bool:
        try:
            database().pyrebase_auth.create_user_with_email_and_password(email=id, password=pw)
            return True
        except HTTPError as error:
            errorMessage = json.loads(error.args[1])['error']['message']
            print(f'{id} // {errorMessage}')
            return False

    # 인증 메일 전송
    def sendEmail(userToken : str) -> bool:
        try:
            database().pyrebase_auth.send_email_verification(userToken)
            return True
        except Exception as e:
            print(f"인증 메일 전송 오류 : {e}")
            return False
    
    # 회원 가입 db 연동
    def signUP(email:str, pw:str, userInfo) -> dict:
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=email, password=pw)
            database().pyrebase_db_user.child(user['localId']).set(userInfo)
            return {'allow' : True, 'result' : user}
        except Exception as e:
            return {'allow' : False, 'result' : f'회원가입 실패 {e}'}

    # 로그인
    def signIN(id : str, pw : str) -> dict:
        try:
            user = database().pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            return {'allow':True, 'result':user}
        except Exception as e:
            print(f"로그인 실패 : {e}")
            return {'allow':False, 'result':'로그인 시도 중 예기치 못한 오류 발생'}
        
    # 회원 정보 호출
    def showUserInfo(uid : str, token):
        try:
            userInfo = database().pyrebase_db_user.child(uid).get(token=token).val()
            return {'allow':True, 'result':userInfo}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':f'정보 불러오기 실패 {e}'}

    # 비밀번호 변경
    def PWChange(token : str, newPW : str) -> bool:
        try:
            database().pyrebase_auth.change_password(token, newPW)
            return True
        except Exception as e:
            print(f"비밀번호 변경 오류 : {e}")
            return False

    # 비밀번호 연장
    def PWlaterChange(uid : str, date : str) -> bool:
        try:
            results = {
                'createPW' : date
            }
            database().pyrebase_db_user.child(uid).update(results)
            return True
        except Exception as e:
            print(f'비밀번호 연장 실패 {e}')
            return False
    
    # 회원 탈퇴
    def guestOUT():
        pass

    # 사용자 주소 추가
    def addAddr(uid : str, token : str, addAddr : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('address').push(data=addAddr, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 사용자 주소 삭제
    def delAddr(uid : str, token : str, delAddr : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('address').child(delAddr).remove(token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 주 배송지 수정
    def homeAddr(uid : str, token : str, addr : str, delAddr : str) -> bool:
        try:
            oldAddr = database().pyrebase_db_user.child(uid).child('address').child('home').get(token=token).val()
            database().pyrebase_db_user.child(uid).child('address').push(data=oldAddr, token=token)
            database().pyrebase_db_user.child(uid).child('address').update(data={'home':addr}, token=token)
            database().pyrebase_db_user.child(uid).child('address').child(delAddr).remove(token=token)
            return True
        except Exception as e:
            print(e)
            return False


class items(database):
    # 아이템 수량 및 상태    
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus = database().pyrebase_db_itemStatus.child(itemId).get().val()
            return {'allow':True, 'result':itemStatus}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':'아이템 조회 실패'}

    # 아이템 ID 리스트
    def itemsIdList():
        itemsId_dict = database().pyrebase_db_items.get().val()
        itemsId = list(itemsId_dict.keys())
        return itemsId

    # 아이템 구매 및 상태 변경
    def itemOrder(uid : str, token : str, itemID : str, orderTime : str, address : str) -> bool:
        try:
            database().pyrebase_db_orderList.child(f'{uid}{orderTime}').set(
                data={
                    'item':itemID,
                    'address' : address,
                    'status' : 'ready'
                    },
                token=token
            )
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get(token=token).val()
            countResults = int(itemStatus['count']) - 1
            if countResults <= 10:
                itemResults = {
                    'count' : countResults,
                    'enable' : False
                }
                database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults,token=token)
                return True
            else:
                itemResults = {
                    'count' : countResults
                }
                database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults,token=token)
                return True
        except Exception as e:
            print(f'상품 주문 실패 {e}')
            return False

    # 주문 내역 불러오기
    def showOrderList(uid : str, token : str) -> dict:
        try:
            myOrderQuery = database().pyrebase_db_orderList.order_by_value().start_at(start=uid)
            myOrder = myOrderQuery.get(token=token)
            return {'allow':True, 'result':myOrder}
        except Exception as e:
            print(e)
            return {'allow':False, 'result':f'주문 내역 조회 실패 {e}'}

    # 배송지 변경
    def cgAddr(uid : str, token : str, key : str, addr : str) -> bool:
        try:
            database().pyrebase_db_orderList.child(uid).child('orderList').child(key).update(data={'address':addr}, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 주문 취소 및 환불
    def orderCancel(uid : str, token : str, key : str, itemID : str):
        try:
            database().pyrebase_db_user.child(uid).child('orderList').child(key).update(data={'status':'cancel'}, token=token)
            itemStatus = database().pyrebase_db_itemStatus.child(itemID).get(token=token).val()
            countResults = int(itemStatus['count']) + 1
            if itemStatus['enable']:
                itemResults = {
                    'count' : countResults
                }
            else:
                if countResults > 10:
                    itemResults = {
                        'count' : countResults,
                        'enable' : True
                    }
                else:
                    itemResults = {
                        'count' : countResults
                    }
            database().pyrebase_db_itemStatus.child(itemID).update(data=itemResults, token=token)
            return True
        except Exception as e:
            print(e)
            return False

    # 환불 요청
    def orderRefund(uid : str, token : str, key : str) -> bool:
        try:
            database().pyrebase_db_user.child(uid).child('orderList').child(key).update(data={'status':'refund'}, token=token)
            return True
        except Exception as e:
            print(e)
            return False


# 주소 검색
def seachAddress(address : str):
    sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]
    if re.search(r"[\]\[%;<>=]", address):
        return {'allow':False, 'result':'특수문자는 포함할 수 없습니다.'}
    elif any(i in address.upper() for i in sqlInjection):
        return {'allow':False, 'result':'포함할 수 없는 단어가 존재합니다.'}
    else:
        addressKey = {
            "confmKey" : st.secrets["address_search"]["keys"],
            "currentPage" : 1,
            "countPerPage" : 10,
            "keyword" : address,
            "resultType" : "json"
        }
        try:
            response = requests.post("https://business.juso.go.kr/addrlink/addrLinkApi.do", data=addressKey)
            if response.status_code == 200:
                addrLen = response.json()["results"]["juso"].__len__()
                if addrLen == 0:
                    return {'allow':False, 'result':'주소가 없습니다.'}
                else:
                    addrList = []
                    for i in range(addrLen):
                        addrList.append(response.json()["results"]["juso"][i]["zipNo"] + ' ' + response.json()["results"]["juso"][i]["roadAddr"])
                    return {'allow':True, 'result':addrList}
        except Exception:
            return {'allow':False, 'result':'주소 검색 실패, 다시 시도해주세요.'}