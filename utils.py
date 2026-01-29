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
import io
from streamlit.runtime.scriptrunner import add_script_run_ctx

@st.cache_data(ttl=36000)
def load_and_optimize_from_url(url, quality=85):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        input_bytes = io.BytesIO(response.content)
        img = Image.open(input_bytes)

        if img.mode == "P":
            img = img.convert("RGBA")

        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=quality)
        
        b64_data = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/webp;base64,{b64_data}"

    except Exception as e:
        print(f"이미지 로드 중 오류 발생: {e}") 
        return None

@st.cache_data(ttl=36000)
def load_raw_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # MIME 타입 추론 (헤더 기반)
        content_type = response.headers.get('Content-Type')
        if not content_type or 'image' not in content_type:
            # URL 파싱하여 확장자 확인 (Query Param 제외)
            from urllib.parse import urlparse
            path = urlparse(url).path
            
            # 기본값 또는 확장자로 추론 (WebP/PNG)
            if path.lower().endswith('.png'):
                content_type = 'image/png'
            else:
                content_type = 'image/webp'
        
        b64_data = base64.b64encode(response.content).decode()
        return f"data:{content_type};base64,{b64_data}"

    except Exception as e:
        print(f"이미지 로드 실패: {e}")
        return None

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
        self.firestore_vanner = {}
        self.firestore_item = {}
        self.firestore_code = {}
        
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

        # 2. 코드(그룹) 이미지 로딩
        try:
            codeSnapshot = self.fs_client.collection('code').stream()
            for doc in codeSnapshot:
                data = doc.to_dict()
                if data:
                    self.firestore_code[doc.id] = data
        except Exception as e:
            print(f"코드 정보 로딩 실패: {e}")

        # 3. 아이템 로딩
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
            
            # 별도 스레드에서 프리캐싱 시작 (서버 시작 시 1회 수행됨)
            precache_thread = threading.Thread(target=self._precache_images, args=(new_items,), daemon=True)
            add_script_run_ctx(precache_thread)
            precache_thread.start()

        except Exception as e:
            print(f"아이템 목록 로딩 실패: {e}")

    def _precache_images(self, item_dict):
        print("이미지 프리캐싱 시작...")
        
        # Code 이미지 프리캐싱
        if self.firestore_code:
            for key, val in self.firestore_code.items():
                try:
                    if val.get('path'):
                        load_and_optimize_from_url(str(val['path']))
                except Exception:
                    continue

        count = 0
        for key, item_data in item_dict.items():
            try:
                # 상품 이미지 (paths)
                if item_data.paths:
                    for path in item_data.paths:
                        load_and_optimize_from_url(str(path))
                        # 리스트용 썸네일도 캐싱 (quality=80)
                        load_and_optimize_from_url(str(path), quality=80)
                
                # 상세 이미지 (detail)
                if item_data.detail:
                    load_raw_image_from_url(str(item_data.detail))
                    
                count += 1
            except Exception:
                continue
                
        print(f"이미지 프리캐싱 완료 ({count}개 아이템 처리됨)")

    def refresh_items(self):
        """아이템 정보를 강제로 새로고침합니다."""
        print("아이템 정보 새로고침 시작...")
        self._load_items()
        print("아이템 정보 새로고침 완료")

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

    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stExpandSidebarButton"] {{
        background-color: #8D6E63 !important;
        color: #FFFEFA !important;
        border: none !important;
        border-radius: 4px !important;
        z-index: 1000000 !important;
    }}

    [data-testid="stSidebarCollapsedControl"] *,
    [data-testid="stExpandSidebarButton"] * {{
        color: #FFFEFA !important;
        fill: #FFFEFA !important;
        stroke: #FFFEFA !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"],
    [data-testid="stCollapseSidebarButton"],
    [data-testid="stSidebarCollapseButton"] {{
        background-color: #8D6E63 !important;
        color: #F5F0EB !important;
        border: none !important;
        border-radius: 4px !important;
        opacity: 1 !important;
        visibility: visible !important;
        display: flex !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stBaseButton-headerNoPadding"] *,
    [data-testid="stCollapseSidebarButton"] *,
    [data-testid="stSidebarCollapseButton"] * {{
        color: #F5F0EB !important;
        fill: #F5F0EB !important;
    }}

    section[data-testid="stSidebar"] > div > div:first-child {{
        opacity: 1 !important; 
        visibility: visible !important;
    }}
    </style>
    """

    st.html(common_css)

def set_sidebar():

    st.divider()

    st.markdown(body='### products')

    newBTN = st.button(
        label='new',
        type='tertiary',
        icon=':material/auto_awesome:',
        width='content'
    )
    glassesBTN = st.button(
        label='glasses',
        type='tertiary',
        icon=':material/eyeglasses_2:',
        width='content'
    )
    sunglassesBTN = st.button(
        label='sunglasses',
        type='tertiary',
        icon=':material/sunny:',
        width='content'
    )
    sportyBTN = st.button(
        label='goggles',
        type='tertiary',
        icon=':material/head_mounted_device:',
        width='content'
    )

    if newBTN:
        st.session_state.page = 'new'
        st.switch_page(page='pages/9itemList.py')
    if glassesBTN:
        st.session_state.page = 'glasses'
        st.switch_page(page='pages/9itemList.py')
    if sunglassesBTN:
        st.session_state.page = 'sunglasses'
        st.switch_page(page='pages/9itemList.py')
    if sportyBTN:
        st.session_state.page = 'sporty'
        st.switch_page(page='pages/9itemList.py')

    st.divider()

    if st.button(
        label='이벤트 및 공지사항',
        type='tertiary',
        icon='📢',
        width='content'
    ):
        st.switch_page(body='pages/0notice.py')

    if st.button(
        label='문의하기',
        type='tertiary',
        icon='🎧',
        width='content'
    ):
        st.switch_page(body='pages/0cs.py')

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