import streamlit as st
import pyrebase
import re
import requests.exceptions
import json
import firebase_admin
from firebase_admin import auth, credentials, firestore


"""
# FireBase secret_keys
secretKeyPath = {
    "type" : st.secrets["firebaseKey"]["type"],
    "project_id" : st.secrets["firebaseKey"]["project_id"],
    "private_key_id" : st.secrets["firebaseKey"]["private_key_id"],
    "private_key" : st.secrets["firebaseKey"]["private_key"],
    "client_email" : st.secrets["firebaseKey"]["client_email"],
    "client_id" : st.secrets["firebaseKey"]["client_id"],
    "auth_uri" : st.secrets["firebaseKey"]["auth_uri"],
    "token_uri" : st.secrets["firebaseKey"]["token_uri"],
    "auth_provider_x509_cert_url" : st.secrets["firebaseKey"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url" : st.secrets["firebaseKey"]["client_x509_cert_url"],
    "universe_domain" : st.secrets["firebaseKey"]["universe_domain"]
    }

# Firebase 앱이 이미 초기화되었는지 확인
if not firebase_admin._apps:
    try:
        path = credentials.Certificate(cert=secretKeyPath)
        firebase_admin.initialize_app(credential=path)
        print("FireBase Admin SDK 앱 초기화 완료 (from utils.py)")
    except Exception as e:
        print(f"Firebase Admin SDK 초기화 오류 in utils.py: {e}")
"""

# Firebase 사용자 keys
firebaseWebConfig = {
    "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
    "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
    "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
    "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
    "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
    "appId" : st.secrets["firebaseWebConfig"]["appId"],
    "databaseURL" : None
    }

# pyrebase - firebase 연결
firebase = pyrebase.initialize_app(config=firebaseWebConfig)

# guest 관리
class guest:
    def __init__(self):
        self.pyrebase_auth = firebase.auth() # 회원 인증
        self.pyrebase_db_user = firebase.database().child('user') # 회원 정보 db

    # 회원 가입 전 중복 이메일 검증
    def emailCheck(self, id : str):
        try:
            if self.pyrebase_db_user.child(id).get() is None:
                return True
            else:
                return False
        except Exception as e:
            print(f'이메일 중복확인 실패 {e}')
            return False
    
    # 회원 가입 db 연동
    def signUP(self, id : str, pw : str, userInfo):
        try:
            self.pyrebase_auth.create_user_with_email_and_password(email=id, password=pw)
            self.pyrebase_db_user.child(id).set(userInfo)
            return True
        except Exception as e:
            print(f"가입 시도 중 예상치 못한 오류 발생: {e}")
            return False

    # 로그인
    def signIN(self, id : str, pw : str):
        try:
            user = self.pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
            userInfo = self.pyrebase_db_user.child(user['--']).get()
            return userInfo
        except Exception as e:
            print(f'로그인 실패 {e}')
            return False

    # 로그아웃
    def signOUT(self):
        try:
            return st.session_state.clear
        except Exception as e:
            print(f'로그아웃 실패 {e}')
            return False

    def PWlaterChange(self, id : str, date : str):
        try:
            results = {
                'createPW' : date
            }
            self.pyrebase_db_user.child(id).update(results)
            return True
        except Exception as e:
            print(f'비밀번호 연장 실패 {e}')
            return False
    
    # 회원 탈퇴
    def guestOUT(self):
        pass


class items:
    def __init__(self):
        self.pyrebase_db_items = firebase.database().child('items')
        self.pyrebase_db_itemCount = firebase.database().child('itemCount')
        self.pyrebase_db_user = firebase.database().child('user')
    
    # 아이템 수량 및 상태    
    def itemStatus(self, itemId : str):
        try:
            itemStatus = self.pyrebase_db_itemCount.child(itemId).get() # 아이템 상태 조회
            return itemStatus
        except Exception as e:
            print(f'아이템 상태 조회 실패 {e}')
            return False
    
    # 아이템 ID 리스트
    def itemsIdList(self):
        itemsId_dict = self.pyrebase_db_items.shallow().get().val() # 아이템 키값 dict {'items1':True}
        itemsId = list(itemsId_dict.keys()) # 아이템 키값 list
        return itemsId

    # 아이템 like 상태 (고객 info로 따라감)
    def itemsLike(self, id : str, userInfo : dict, like : str):
        try:
            if like in userInfo['like']:
                userInfo['like'].remove(like)
                results = {
                    'like' : userInfo['like']
                }
                self.pyrebase_db_user.child(id).update(results)
                return True
            else:
                userInfo['like'].append(like)
                results = {
                    'like' : userInfo['like']
                }
                self.pyrebase_db_user.child(id).update(results)
                return True
        except Exception as e:
            print(f'like 실패 {e}')
            return False

    # 아이템 구매 및 상태 변경
    def itemOrder(self, id : str, itemId : str):
        try:
            userInfo = self.pyrebase_db_user.child(id)
            orderList = userInfo.get()['orderList']
            orderResults = orderList.append(itemId)
            userResults = {
                'orderList' : orderResults
            }
            userInfo.update(userResults) # 고객 주문 내역에 추가
            itemStatus = self.pyrebase_db_itemCount.child(itemId) # 아이템 수량 변경
            countResults = int(itemStatus.get()['count']) - 1
            if countResults < 4:
                itemResults = {
                    'count' : countResults,
                    'enable' : False
                }
                itemStatus.update(itemResults)
                return True
            else:
                itemResults = {
                    'count' : countResults
                }
                itemStatus.update(itemResults)
                return True
        except Exception as e:
            print(f'상품 주문 실패 {e}')
            return False


# 주소 검색
def seachAddress(address : str):
    sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]
    if re.search(r"[\]\[%;<>=]", address):
        st.error(body="특수문자는 포함할 수 없습니다.")
    elif any(i in address.upper() for i in sqlInjection):
        st.error(body="포함할 수 없는 단어가 존재합니다.")
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
                    return '검색 결과가 없습니다. 주소를 다시 확인해주세요.'
                else:
                    for i in range(addrLen):
                        st.write(response.json()["results"]["juso"][i]["zipNo"])
                        st.write(response.json()["results"]["juso"][i]["roadAddr"])
                        choise = st.button(
                            label="선택",
                            key=f"choise{i}"
                        )
                        if choise:
                            return response.json()['results']['juso'][i]['roadAddr']
        except Exception as e:
            st.error(f'주소 검색 실패 {e}')
            return False

"""
# firestore 연결
db = firestore.client()
logoDB = db.collection('logo') # 로고 정보 가져오기
itemsDB = db.collection('items') # items 컬렉션 연결
userInfoDB = db.collection('userInfo')
orderDB = db.collection('orderList')

# 상품 추가 함수
def addItem(item_data, item_id):
    try:
        if item_id:
            item_data_to_set = item_data.copy()
            item_data_to_set['id'] = item_id
            itemsDB.document(item_id).set(item_data_to_set)
            print(f"상품 '{item_id}'이(가) Firestore에 성공적으로 설정되었습니다.")
            return item_id
        else:
            print("상품 ID 미지정, 실패")
            return None
    except Exception as e:
        print(f"Firestore에 상품을 추가/설정하는 중 오류 발생: {e}")
        return None

# 사용자 orders status 수정_배송중
def deliveryStatus(orderStatus:list):
    try:
        allUsers = userInfoDB.stream()
        for user in allUsers:
            orderLists = user.get().to_dict()["orders"]
            for orderList in orderLists:
                if orderList in orderStatus:
                    orderDelivery = orderList + "/" + "delivery"
                    orderLists.remove(orderList)
                    orderLists.append(orderDelivery)
                else:
                    pass
            userInfoDB.document(user.id).update({"orders":orderLists})
    except Exception:
        print("배송 상태 업데이트 오류")

# 사용자 orders status 수정_완료
def completeStatus(orderStatus:list):
    try:
        allUsers = userInfoDB.stream()
        for user in allUsers:
            orderLists = user.get().to_dict()["orders"]
            for orderList in orderLists:
                if orderList in orderStatus:
                    orderComplete = orderList.replace("delivery", "complete")
                    orderLists.remove(orderList)
                    orderLists.append(orderComplete)
                else:
                    pass
            userInfoDB.document(user.id).update({"orders":orderLists})
    except Exception:
        print("완료 상태 업데이트 오류")
"""