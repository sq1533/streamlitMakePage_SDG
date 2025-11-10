import streamlit as st
import firebase_admin
from firebase_admin import db, firestore

from schema.schema import item

@st.cache_resource()
def firebaseInitializeApp():
    private_key = st.secrets["firebaseKey"]["private_key"].replace('\\n', '\n')
    
    firebaseKey = {
        "type" : st.secrets["firebaseKey"]["type"],
        "project_id" : st.secrets["firebaseKey"]["project_id"],
        "private_key_id" : st.secrets["firebaseKey"]["private_key_id"],
        "private_key" : private_key, # 수정된 private_key 사용
        "client_email" : st.secrets["firebaseKey"]["client_email"],
        "client_id" : st.secrets["firebaseKey"]["client_id"],
        "auth_uri" : st.secrets["firebaseKey"]["auth_uri"],
        "token_uri" : st.secrets["firebaseKey"]["token_uri"],
        "auth_provider_x509_cert_url" : st.secrets["firebaseKey"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url" : st.secrets["firebaseKey"]["client_x509_cert_url"],
        "universe_domain" : st.secrets["firebaseKey"]["universe_domain"]
    }

    if not firebase_admin._apps:
        cred = firebase_admin.credentials.Certificate(firebaseKey)
        firebase_admin.initialize_app(
            credential=cred,
            options={'databaseURL' : st.secrets["firebaseKey"]["databaseURL"]}
        )

firebaseInitializeApp()

class database:
    def __init__(self):
        fs_client = firestore.client()
        # firestore 배너
        self.firestore_vanner : dict = {}
        vannerSnapshot = fs_client.collection('vanner').stream()
        for doc in vannerSnapshot.items():
            data = doc.to_dict()
            self.firestore_vanner[data.keys()] = data.values()

        # firestore 아이템 수집
        self.firestore_item : dict = {}
        itemSnapshot = fs_client.collection('item').stream()
        for doc in itemSnapshot.items():
            data = doc.to_dict()
            if not data:
                continue
            try:
                itemData = item(data.values())
                self.firestore_item[doc.id] = itemData
            except Exception as e:
                print(f'파싱 오류 {doc.id} : {e}')
        
        # realtime DB 호출
        self.realtimeDB = db

        # SQL 인젝션 방어 키워드
        self.sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]

        # email 발송 keys
        self.emailAccess = {
            'SENDER_EMAIL':st.secrets["email_credentials"]["sender_email"],
            'SENDER_APP_PASSWORD':st.secrets["email_credentials"]["sender_password"],
            'SENDER_SERVER':st.secrets["email_credentials"]["smtp_server"],
            'SENDER_PORT':st.secrets["email_credentials"]["smtp_port"],
            'DEPLOYED_BASE_URL':st.secrets["email_credentials"]["base_url"]
        }

        # 주문 상태 메세지
        self.showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료',
                'Done':'배송 완료',
                'cancel':'취소 완료',
                'refund':'환불 요청 완료',
                'refunded':'환불 완료'
            }

        # 약관 및 정보
        with open(file='database/condition.txt', mode='r', encoding='utf-8') as file:
            self.condition = file.read()
        with open(file='database/infoUsed.txt', mode='r', encoding='utf-8') as file:
            self.infoUsed = file.read()
        with open(file='database/infoAdmin.txt', mode='r', encoding='utf-8') as file:
            self.infoAdmin = file.read()

# utils.py 전역에 싱글톤 인스턴스 관리
_db_instance = None

def db() -> database:
    global _db_instance
    if _db_instance is None:
        _db_instance = database()
    return _db_instance