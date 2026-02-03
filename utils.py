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
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 텔레그램 로그 핸들러
class TelegramLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        try:
            self.bot_token = st.secrets["telegram"]["bot_token"]
            self.error_chat_id = st.secrets["telegram"]["error_chat_id"]
            self.user_request_id = st.secrets["telegram"]["user_request_id"]
        except Exception:
            self.bot_token = None
            self.error_chat_id = None
            self.user_request_id = None

    def emit(self, record):
        if not self.bot_token or not self.error_chat_id:
            return

        log_entry = self.format(record)

        def send_msg():
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id':self.error_chat_id,
                'text':f'[CRITICAL ERROR]\n\n{log_entry}',
                'parse_mode':'HTML'
            }
            try:
                requests.post(url, data=data, timeout=5)
            except Exception:
                pass 

        thread = threading.Thread(target=send_msg)
        add_script_run_ctx(thread)
        thread.start()
    


# 일반 알림 전송 (환불, 교환 등)
def send_telegram_message(msg: str):
    try:
        bot_token = st.secrets["telegram"]["bot_token"]
        user_request_id = st.secrets["telegram"]["user_request_id"]
    except Exception:
        return

    def send_msg():
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': user_request_id,
            'text': str(msg),
            'parse_mode': 'HTML'
        }
        try:
            requests.post(url, data=data, timeout=5)
        except Exception:
            pass

    thread = threading.Thread(target=send_msg)
    add_script_run_ctx(thread)
    thread.start()

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

    # 2. 텔레그램 핸들러 (ERROR 레벨만)
    t_handler = TelegramLogHandler()
    t_handler.setLevel(logging.ERROR)
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
        self.firestore_item = {}
        self.firestore_code = {}
        
        # 데이터 로딩 실행
        self._load_data()
        self._load_configs()

    def _load_data(self):
        if not self.fs_client: return

        # 1. 코드(그룹) 이미지 로딩
        try:
            codeSnapshot = self.fs_client.collection('code').stream()
            for doc in codeSnapshot:
                data = doc.to_dict()
                if data:
                    self.firestore_code[doc.id] = data
        except Exception as e:
            print(f"코드 정보 로딩 실패: {e}")

        # 2. 아이템 로딩
        self._load_items()

    def _load_items(self):
        try:
            itemSnapshot = self.fs_client.collection('item').stream()
            new_items = {}
            for doc in itemSnapshot:
                data = doc.to_dict()
                if data:
                    try:
                        itemData = item(**data) # 스키마 적용
                        new_items[doc.id] = itemData

                    except Exception as e:
                        print(f"아이템 파싱 오류 {doc.id}: {e}")

            self.firestore_item = new_items
            
        except Exception as e:
            print(f"아이템 목록 로딩 실패: {e}")

    def refresh_items(self):
        """아이템 정보를 강제로 새로고침합니다."""
        print("아이템 정보 새로고침 시작...")
        self._load_items()
        print("아이템 정보 새로고침 완료")

    def _load_configs(self):
        # 페이지 icon
        try:
            self.pageIcon = Image.open('database/icon.webp')
        except:
            self.pageIcon = None
        
        try:
            with open('database/nav.webp', "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                self.logo_base64 = f"data:image/webp;base64,{encoded_string}"
        except Exception as e:
            self.logo_base64 = ""
            print(f"로고 로딩 실패: {e}")

        try:
            with open('database/navSide.webp', "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
                self.logo_side_base64 = f"data:image/webp;base64,{encoded_string}"
        except Exception as e:
            self.logo_side_base64 = ""
            print(f"사이드 로고 로딩 실패: {e}")

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
    common_css = f"""
    <style>
    [data-testid="stHeaderActionElements"] {{
        display: none !important;
    }}

    div[data-testid="stElementToolbar"] {{
        display: none !important;
    }}
    
    [data-testid="stIcon"], .material-icons, .material-symbols-rounded {{
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }}

    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {{
        background-color: #eaeaea !important;
        color: #F5F0EB !important;
        border: none !important;
        border-radius: 4px !important;
        z-index: 1000000 !important;
    }}

    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stExpandSidebarButton"] * {{
        color: #121212 !important;
        fill: #121212 !important;
        stroke: #121212 !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stCollapseSidebarButton"],
    [data-testid="stSidebarCollapseButton"] {{
        background-color: #eaeaea !important;
        color: #121212 !important;
        border: none !important;
        border-radius: 4px !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] *,
    [data-testid="stCollapseSidebarButton"] *,
    [data-testid="stSidebarCollapseButton"] * {{
        color: #121212 !important;
        fill: #121212 !important;
    }}

    section[data-testid="stSidebar"] > div > div:first-child {{
        opacity: 1 !important; 
        visibility: visible !important;
    }}
    </style>
    """

    st.html(common_css)

def set_sidebarLogo():
    logo_html = f"""
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <a href="https://amuredo.shop" target="_self" style="width: 100%; display: flex; justify-content: center; text-decoration: none;">
                <img src="{utilsDb().logo_side_base64}" style="width: 100%; max-width: 280px; height: auto; object-fit: contain;">
            </a>
        </div>
    """
    st.html(logo_html)

def set_sidebar():    
    st.divider()

    if st.button(
        label='NEW',
        type='tertiary',
        width='content'
    ):
        st.session_state.page = 'new'
        st.switch_page(page='pages/9itemList.py')
    if st.button(
        label='BEST',
        type='tertiary',
        width='content'
    ):
        st.session_state.page = 'best'
        st.switch_page(page='pages/9itemList.py')
    if st.button(
        label='Glasses',
        type='tertiary',
        width='content'
    ):
        st.session_state.page = 'glasses'
        st.switch_page(page='pages/9itemList.py')
    if st.button(
        label='Sunglasses',
        type='tertiary',
        width='content'
    ):
        st.session_state.page = 'sunglasses'
        st.switch_page(page='pages/9itemList.py')
    if st.button(
        label='Goggles',
        type='tertiary',
        width='content'
    ):
        st.session_state.page = 'sporty'
        st.switch_page(page='pages/9itemList.py')

    st.divider()

    if st.button(
        label='이벤트 및 공지사항',
        type='tertiary',
        width='content'
    ):
        st.switch_page(page='pages/0notice.py')
    if st.button(
        label='문의하기',
        type='tertiary',
        width='content'
    ):
        st.switch_page(page='pages/0cs.py')

    st.divider()

    aboutBTN = st.button(
        label='about us',
        type='tertiary',
        width='content'
    )
    if aboutBTN:
        st.switch_page(page='pages/9about.py')

# utils.py 전역에 싱글톤 인스턴스 관리
_db_instance = None

def utilsDb() -> database:
    global _db_instance
    if _db_instance is None:
        _db_instance = database()
    return _db_instance