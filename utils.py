import streamlit as st
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
logo_data = logoDB.document('logo').get().to_dict() # logo 위젯과의 충돌을 피하기 위해 logo_data로 변경
itemsDB = db.collection('items') # items 컬렉션 연결