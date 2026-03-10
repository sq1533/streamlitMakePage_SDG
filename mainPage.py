import streamlit as st
import mimetypes
mimetypes.add_type('text/html', '.html')
mimetypes.add_type('application/javascript', '.js')

import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

# 페이지 세션 관리
if 'item' not in st.session_state:
    st.session_state.item = {
        'item' : '',
        'itemKey' : 0
    }

if 'vannerKey' not in st.session_state:
    st.session_state.vannerKey = 0

# vannerCode > dict
vannerData : dict = utils.database().firestore_code
vanner = list(vannerData.keys())

showcaseKey : str = vanner[st.session_state.vannerKey]
showcase : dict = vannerData.get(showcaseKey)

st.html(
    """
    <style>
    .showcase-img-container {
        width: 100%;
        aspect-ratio: 5 / 3;
        overflow: hidden;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }
    .showcase-img-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .showcase-title {
        color: #0E3A5B;
        font-weight: 800;
        font-size: 1.5rem;
        margin-bottom: 10px;
        text-align: center;
    }
    .showcase-desc {
        color: #555;
        line-height: 1.6;
        font-size: 1.05rem;
        word-break: keep-all;
        display: -webkit-box;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-align: center;
    }
    </style>
    """
)

sc_left, sc_right = st.columns(spec=2, gap="medium", vertical_alignment="center")

with sc_left.container():
    img_url = str(showcase.get('path', ''))
    gif_bg_url = utils.utilsDb().waiting_gif_base64
    
    st.html(f'''
        <div class="showcase-img-container" style="background: url('{gif_bg_url}') center center no-repeat; background-size: cover; background-color: #F8F9FA;">
            <img src="{img_url}">
        </div>
    ''')

    with st.container(horizontal=True):
        if st.button('◀ before', type='secondary', width=100):
            st.session_state.vannerKey = (st.session_state.vannerKey - 1) % len(vanner)
            st.rerun()

        st.space(size='stretch')

        if st.button('next ▶', type='secondary', width=100):
            st.session_state.vannerKey = (st.session_state.vannerKey + 1) % len(vanner)
            st.rerun()

with sc_right:
    sc_name = showcase.get('name', '대표 상품 이름')
    sc_text = showcase.get('info', '이곳에 상품에 대한 상세한 설명이 들어갑니다.')

    st.html(
        body=f'''
        <div style="padding: 20px 0;">
            <div class="showcase-title">{sc_name}</div>
            <div class="showcase-desc">{sc_text}</div>
        </div>
    ''')
    with st.container(horizontal=True):
        st.space(size='stretch')
        if st.button('상세보기', type='primary', width='stretch'):
            st.session_state.item['item'] = showcaseKey
            st.session_state.item['itemKey'] = 0
            st.switch_page(page='pages/7item.py')
        st.space(size='stretch')

st.divider()

# 브랜드 카피라이트 및 철학
brandStory, brandColor = st.columns(spec=[2,1], gap='small', vertical_alignment='top',width='stretch')

brandStory.html(
    body="""
    <style>
    .grid-left {
        background-color: #F8F9FA;
        padding: 40px 30px;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.25);
        height: 100%;
    }
    </style>

    <div class="grid-left">
        <h2 style='color: #0E3A5B; font-weight: 800; font-family: "Outfit", sans-serif; letter-spacing: -1px; margin-bottom: 20px;'>
            That's it, AMUREDO
        </h2>
        <div style="text-align: center; line-height: 1.8; color: #444; font-size:1.05rem; word-break: keep-all;">
            <b>AMUREDO</b>는 안경을 단순한 패션 아이템이 아닌,<br>
            당신의 능률을 끌어올릴 <b>최고의 오피스 기어</b>로 정의합니다.<br><br>
            모니터 앞에서의 치열한 컴퓨터 작업부터 출퇴근 길의 운전까지.<br>
            당신은 그저 일에만 집중하세요.<br>
            시야의 편안함은 아무래도가 책임지겠습니다.
        </div>
    </div>
    """
)
brandColor.html(
    body="""
    <style>
    .grid-right {
        display: flex;
        flex-direction: column;
        gap: 20px;
        height: 100%;
    }
    .grid-right-top, .grid-right-bottom {
        flex: 1;
        border-radius: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 30px;
    }
    .grid-right-bottom {
        background-color: #0E3A5B;
        color: white;
    }
    </style>

    <div class="grid-right">
        <div class="grid-right-top">
            <div>
                <h4 style="color:#0E3A5B; margin-bottom:10px; font-weight:700;">아무래도 브랜드 철학</h4>
                <p style="color:#555; font-size:0.95rem; margin:0;">
                    눈의 피로가<br>당신의 하루를 망칠 수 없도록.
                </p>
            </div>
        </div>
        <div class="grid-right-bottom">
            <h4 style="color:#ffffff; font-weight:700; opacity:0.9;">시그니처 컬러<br>딥 네이비</h4>
        </div>
    </div>
    """
)

# brand keywords 스타일
st.html(
    body="""
    <style>
    @keyframes toastPopup {
        0% { opacity: 0; transform: translateY(40px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    .feature-card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        height: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        opacity: 0;
        animation: toastPopup 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
    }
    .delay-1 { animation-delay: 1s; }
    .delay-2 { animation-delay: 2s; }
    .delay-3 { animation-delay: 3s; }
    .delay-4 { animation-delay: 4s; }
    .feature-icon {
        font-size: 2em;
        margin-bottom: 10px;
    }
    .feature-title {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
        color: #0E3A5B;
    }
    .feature-desc {
        color: #555555;
        font-size: 0.9em;
        line-height: 1.5;
        word-break: keep-all; /* 단어 단위로 줄바꿈 허용 */
    }
    </style>
    """
)

# 4개의 기능 카드 (2x2 그리드)
col1, col2 = st.columns(2)

with col1:
    st.html(
        """
        <div class="feature-card delay-1">
            <div class="feature-icon">☁️</div>
            <div class="feature-title">Comfortable Fit</div>
            <div class="feature-desc">
                마치 쓰지 않은 듯한 편안함. 인체 공학적 패턴으로 최상의 착용감을 선사합니다.
            </div>
        </div>
        """
    )
    
with col2:
    st.html(
        """
        <div class="feature-card delay-2">
            <div class="feature-icon">💎</div>
            <div class="feature-title">Reasonable Price</div>
            <div class="feature-desc">
                불필요한 유통 과정을 줄여 누구나 부담 없이 즐길 수 있는 합리적인 가격을 제안합니다.
            </div>
        </div>
        """
    )

col3, col4 = st.columns(2)

with col3:
    st.html(
        """
        <div class="feature-card delay-3">
            <div class="feature-icon">🍃</div>
            <div class="feature-title">Light Weight</div>
            <div class="feature-desc">
                하루 종일 써도 피로하지 않은 가벼운 소재를 사용하여 활동성을 극대화했습니다.
            </div>
        </div>
        """
    )
    
with col4:
    st.html(
        """
        <div class="feature-card delay-4">
            <div class="feature-icon">✨</div>
            <div class="feature-title">Simple Design</div>
            <div class="feature-desc">
                유행을 타지 않는 미니멀하고 심플한 디자인으로 오래도록 사랑받는 스타일입니다.
            </div>
        </div>
        """
    )

# 오프라인 위치
st.html(
    body="""
    <style>
    .offline-store-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #0E3A5B;
        color: #ffffff !important;
        text-decoration: none;
        padding: 18px 40px;
        border-radius: 12px;
        font-size: 1.4rem;
        font-weight: 800;
        box-shadow: 0 4px 10px rgba(14, 58, 91, 0.2);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin: 20px auto;
        max-width: 400px;
        width: 90%;
        gap: 12px;
    }
    .offline-store-btn:hover {
        background-color: #144f7a;
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(14, 58, 91, 0.3);
        color: #ffffff !important;
    }
    .offline-store-btn:active {
        transform: translateY(0px);
        box-shadow: 0 4px 10px rgba(14, 58, 91, 0.2);
    }
    </style>
    <div style="display: flex; justify-content: center; width: 100%; margin: 30px 0;">
        <a href="https://naver.me/FiPl0mEN" target="_blank" class="offline-store-btn">
            🌍 오프라인 스토어
        </a>
    </div>
    """
)

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()

st.divider()

policyB = st.button(
    label='개인정보 처리방침',
    type='tertiary',
    width='content'
)
cookiesB = st.button(
    label='쿠키 정책',
    type='tertiary',
    width='content'
)
termsB = st.button(
    label='이용약관',
    type='tertiary',
    width='content'
)

if policyB:
    st.switch_page(page='pages/0policy.py')
if cookiesB:
    st.switch_page(page='pages/0cookies.py')
if termsB:
    st.switch_page(page='pages/0useTerms.py')

st.html(body=utils.utilsDb().infoAdmin)