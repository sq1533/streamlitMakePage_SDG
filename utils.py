import streamlit as st
import firebase_admin
from firebase_admin import db, firestore, credentials
from PIL import Image
import base64
import json

import logging
import threading
import requests
from schema.schema import item

# 텔레그램 로그 핸들러
class TelegramLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        try:
            self.bot_token = st.secrets["telegram"]["bot_token"]
            self.chat_id = st.secrets["telegram"]["chat_id"]
        except Exception:
            self.bot_token = None
            self.chat_id = None

    def emit(self, record):
        if not self.bot_token or not self.chat_id:
            return

        log_entry = self.format(record)

        def send_msg():
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id':self.chat_id,
                'text':f'[CRITICAL ERROR]\n\n{log_entry}',
                'parse_mode':'HTML'
            }
            try:
                requests.post(url, data=data, timeout=5)
            except Exception:
                pass 

        threading.Thread(target=send_msg).start()

def get_logger():
    logger = logging.getLogger('amuredo')
    
    # 중복 핸들러 방지
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.INFO)
    
    # 1. 콘솔 핸들러
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # 2. 텔레그램 핸들러 (CRITICAL 레벨만)
    t_handler = TelegramLogHandler()
    t_handler.setLevel(logging.CRITICAL)
    t_format = logging.Formatter('%(asctime)s - %(message)s')
    t_handler.setFormatter(t_format)
    logger.addHandler(t_handler)
        
    return logger

# 1. Firebase 앱 초기화 (싱글톤 패턴 강화)
@st.cache_resource
def get_firebase_app():
    if firebase_admin._apps:
        return firebase_admin.get_app()

    try:
        firebase_config = st.secrets["firebaseKey"]

        private_key = firebase_config.get("private_key", "")
        if "\\n" in private_key:
            private_key = private_key.replace('\\n', '\n')

        cred_dict = {
            "type": firebase_config.get("type"),
            "project_id": firebase_config.get("project_id"),
            "private_key_id": firebase_config.get("private_key_id"),
            "private_key": private_key,
            "client_email": firebase_config.get("client_email"),
            "client_id": firebase_config.get("client_id"),
            "auth_uri": firebase_config.get("auth_uri"),
            "token_uri": firebase_config.get("token_uri"),
            "auth_provider_x509_cert_url": firebase_config.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": firebase_config.get("client_x509_cert_url"),
            "universe_domain": firebase_config.get("universe_domain")
        }
        cred = credentials.Certificate(cred_dict)
        app = firebase_admin.initialize_app(
            credential=cred,
            options={
                'databaseURL': firebase_config.get("databaseURL")
            }
        )
        return app

    except Exception as e:
        st.error(f"Firebase 초기화 에러: {e}")
        return None

# 앱 초기화 실행
get_firebase_app()

def init_session():
    # 회원 토큰 세션 및 정보 / dict
    if 'token' not in st.session_state:
        st.session_state.token = {'naver': None, 'kakao': None, 'gmail': None}
    if 'user' not in st.session_state:
        st.session_state.user = None

    # 페이지 진입 구분 / str
    if 'page' not in st.session_state:
        st.session_state.page = None

    # 주소 찾기 defult 값 / str
    if 'searchAddr' not in st.session_state:
        st.session_state.searchAddr = None
    # 신규 고객 주소 정보 / str
    if 'firstAddr' not in st.session_state:
        st.session_state.firstAddr = None
    # 상세 주소 정보 / str
    if 'detailAddr' not in st.session_state:
        st.session_state.detailAddr = None

    # 상품 상세페이지 / str
    if 'item' not in st.session_state:
        st.session_state.item = None
    # 주문 상품 / str
    if 'orderItem' not in st.session_state:
        st.session_state.orderItem = None

class database:
    def __init__(self):
        try:
            self.fs_client = firestore.client()
            self.realtimeDB = db
        except Exception as e:
            st.error(f"DB 클라이언트 연결 실패: {e}")
            self.fs_client = None
            self.realtimeDB = None
        
        # 데이터 수집 초기화
        self.firestore_vanner = {}
        self.firestore_item = {}
        
        # 데이터 로딩 실행
        self._load_data()
        self._load_configs()

    def _load_data(self):
        if not self.fs_client: return

        # 1. 배너 로딩
        try:
            vannerSnapshot = self.fs_client.collection('vanner').stream()
            for doc in vannerSnapshot:
                data = doc.to_dict()
                if data:
                    self.firestore_vanner[doc.id] = data
        except Exception as e:
            print(f"배너 로딩 실패: {e}")

        # 2. 아이템 로딩
        try:
            itemSnapshot = self.fs_client.collection('item').stream()
            for doc in itemSnapshot:
                data = doc.to_dict()
                if data:
                    try:
                        itemData = item(**data) # 스키마 적용
                        self.firestore_item[doc.id] = itemData
                    except Exception as e:
                        print(f"아이템 파싱 오류 {doc.id}: {e}")
        except Exception as e:
            print(f"아이템 목록 로딩 실패: {e}")

    def _load_configs(self):
        # 페이지 icon
        try:
            self.pageIcon = Image.open('database/icon.png')
        except:
            self.pageIcon = None

        # SQL 인젝션 방어 키워드
        self.sqlInjection = ["OR", "SELECT", "INSERT", "DELETE", "UPDATE", "CREATE", "DROP", "EXEC", "UNION",  "FETCH", "DECLARE", "TRUNCATE"]

        # email 발송 keys
        try:
            self.emailAccess = {
                'SENDER_EMAIL':st.secrets["email_credentials"]["sender_email"],
                'SENDER_APP_PASSWORD':st.secrets["email_credentials"]["sender_password"],
                'SENDER_SERVER':st.secrets["email_credentials"]["smtp_server"],
                'SENDER_PORT':st.secrets["email_credentials"]["smtp_port"],
                'DEPLOYED_BASE_URL':st.secrets["email_credentials"]["base_url"]
            }
        except Exception:
            self.emailAccess = {}

        # 주문 상태 메세지
        self.showStatus = {
                'ready':'상품 제작 중...',
                'delivery':'상품 배송 중...',
                'complete':'배송 완료',
                'Done':'배송 완료',
                'cancel':'취소 완료',
                'exchange':'교환 요청 완료',
                'exchanged':'교환 완료',
                'refund':'환불 요청 완료',
                'refunded':'환불 완료'
            }

        # 약관 및 정보 (파일 읽기 예외처리 추가)
        self.condition = self._read_file('database/condition.txt')
        self.infoUsed = self._read_file('database/infoUsed.txt')
        self.infoAdmin = self._read_file('database/infoAdmin.txt')

        try:
            with open(file='database/notice.json', mode='r', encoding='utf-8') as file:
                notice_list = json.load(file)
                notice_list.sort(key=lambda x: x['date'], reverse=True)
                self.notice = notice_list
        except:
            self.notice = []

    def _read_file(self, path):
        try:
            with open(path, mode='r', encoding='utf-8') as file:
                return file.read()
        except:
            return ""

def set_page_ui():
    try:
        with open(file='database/Hahmlet-Bold.ttf', mode='rb') as f:
            data = f.read()
            b64_data = base64.b64encode(data).decode()
    except Exception as e:
        print(f"폰트 로딩 오류: {e}")
        b64_data = ""

    common_css = f"""
    <style>
    [data-testid="stHeaderActionElements"] {{
        display: none !important;
    }}
    div[data-testid="stElementToolbar"] {{
        display: none !important;
    }}

    @font-face {{
        font-family:'Hahmlet-Bold';
        src:url(data:font/ttf;base64,{b64_data}) format('truetype');
        font-weight: normal;
        font-style: normal;
    }}

    html, body, p, h1, h2, h3, h4, h5, h6, label, button, input, textarea, div {{
        font-family: 'Hahmlet-Bold', sans-serif;
    }}
    
    [data-testid="stIcon"], .material-icons, .material-symbols-rounded {{
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }}
    </style>
    """

    st.html(common_css)

# utils.py 전역에 싱글톤 인스턴스 관리
_db_instance = None

def utilsDb() -> database:
    global _db_instance
    if _db_instance is None:
        _db_instance = database()
    return _db_instance