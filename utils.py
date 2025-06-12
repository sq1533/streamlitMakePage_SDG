import streamlit as st
from datetime import datetime, timezone, timedelta
import firebase_admin
from firebase_admin import auth, credentials, firestore
import pyrebase

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

# Firebase 사용자 keys
firebaseWebConfig = {
    "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
    "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
    "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
    "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
    "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
    "appId" : st.secrets["firebaseWebConfig"]["appId"],
    "databaseURL" : None # pyrebase는 databaseURL이 없어도 괜찮습니다.
    }

# Firebase 앱이 이미 초기화되었는지 확인
if not firebase_admin._apps:
    try:
        path = credentials.Certificate(cert=secretKeyPath)
        firebase_admin.initialize_app(credential=path)
        print("FireBase Admin SDK 앱 초기화 완료 (from utils.py)")
    except Exception as e:
        print(f"Firebase Admin SDK 초기화 오류 in utils.py: {e}")

# 사용자 auth 연결
firebase = pyrebase.initialize_app(config=firebaseWebConfig)
pyrebase_auth = firebase.auth()
# firestore 연결
db = firestore.client()
logoDB = db.collection('logo') # 로고 정보 가져오기
itemsDB = db.collection('items') # items 컬렉션 연결
userInfoDB = db.collection('userInfo')
orderDB = db.collection('orderList')
now = datetime.now(timezone.utc) + timedelta(hours=9)

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