import streamlit as st
import pyrebase
import firebase_admin
from firebase_admin import auth, db

# firebase client
@st.cache_resource()
def firebaseInitializeApp():
    # Firebase 사용자 keys
    pyrebaseKey = {
        "apiKey" : st.secrets["firebaseWebConfig"]["apiKey"],
        "authDomain" : st.secrets["firebaseWebConfig"]["authDomain"],
        "projectId" : st.secrets["firebaseWebConfig"]["projectId"],
        "storageBucket" : st.secrets["firebaseWebConfig"]["storageBucket"],
        "messagingSenderId" : st.secrets["firebaseWebConfig"]["messagingSenderId"],
        "appId" : st.secrets["firebaseWebConfig"]["appId"],
        "databaseURL" : st.secrets["firebaseWebConfig"]["databaseURL"]
        }

    firebase_client = pyrebase.initialize_app(config=pyrebaseKey)

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
            options={'databaseURL': st.secrets["firebaseWebConfig"]["databaseURL"]}
        )

    return {
        'pyrebase': firebase_client,
        'firebase_auth': auth,
        'firebase_rtDB': db,
    }

firebase = firebaseInitializeApp()

# database
class database:
    def __init__(self):
        self.pyrebase_auth = firebase['pyrebase'].auth()
        self.auth = firebase['firebase_auth']
        self.rtDatabase_user = firebase['firebase_rtDB'].reference(path='user') # 회원 정보 호출
        self.rtDatabase_item = firebase['firebase_rtDB'].reference(path='items') # 아이템 정보
        self.rtDatabase_itemStatus = firebase['firebase_rtDB'].reference(path='itemStatus') # 아이템 상태
        self.rtDatabase_orderList = firebase['firebase_rtDB'].reference(path='orderList') # 회원 주문 정보
        self.emailAccess = {
            'SENDER_EMAIL':st.secrets["email_credentials"]["sender_email"],
            'SENDER_APP_PASSWORD':st.secrets["email_credentials"]["sender_password"],
            'SENDER_SERVER':st.secrets["email_credentials"]["smtp_server"],
            'SENDER_PORT':st.secrets["email_credentials"]["smtp_port"],
            'DEPLOYED_BASE_URL':st.secrets["email_credentials"]["base_url"]
        }
        self.emailMain = f"""
        안녕하세요, TEAM.amuredo 입니다.

        원할한 서비스 이용을 위해 아래 링크를 클릭하여 이메일 인증을 완료해주세요.

        만약 본인이 요청한 것이 아니라면 이 메일을 무시해 주세요. 이 링크는 1시간 동안 유효합니다.

        감사합니다.
        amuredo 팀 드림

        [인증 LINK]
        """
        self.sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]
        self.showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료',
                'Done':'배송 완료',
                'cancel':'취소 완료',
                'refund':'환불 요청 완료',
                'refunded':'환불 완료'
            }