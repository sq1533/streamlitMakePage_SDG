import streamlit as st
import firebase_admin
from firebase_admin import db, firestore
from PIL import Image

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

def init_session():
    # 회원 토큰 세션 및 정보 / dict
    if 'token' not in st.session_state:
        st.session_state.token = {'naver': None, 'kakao': None, 'gmail': None}
    if 'user' not in st.session_state:
        st.session_state.user = None

    # 페이지 진입 구분 / str
    if 'page' not in st.session_state:
        st.session_state.page = None

    # 신규 고객 주소 정보 / str
    if 'firstAddr' not in st.session_state:
        st.session_state.firstAddr = None

    # 상품 상세페이지 / str
    if 'item' not in st.session_state:
        st.session_state.item = None
    # 주문 상품 / str
    if 'orderItem' not in st.session_state:
        st.session_state.orderItem = None

class database:
    def __init__(self):
        fs_client = firestore.client()
        # firestore 배너
        self.firestore_vanner : dict = {}
        vannerSnapshot = fs_client.collection('vanner').stream()
        for doc in vannerSnapshot:
            data : dict = doc.to_dict()
            if not data:
                continue
            try:
                self.firestore_vanner[doc.id] = data
            except Exception as e:
                print(f'파싱 오류 {doc.id} : {e}')

        # firestore 아이템 수집
        self.firestore_item : dict = {}
        itemSnapshot = fs_client.collection('item').stream()
        for doc in itemSnapshot:
            data : dict = doc.to_dict()
            if not data:
                continue
            try:
                itemData = item(**data)
                self.firestore_item[doc.id] = itemData
            except Exception as e:
                print(f'파싱 오류 {doc.id} : {e}')
        
        # realtime DB 호출
        self.realtimeDB = db

        # 페이지 icon
        self.pageIcon = Image.open('database/icon.png')

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

def utilsDb() -> database:
    global _db_instance
    if _db_instance is None:
        _db_instance = database()
    return _db_instance