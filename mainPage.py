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

import api
import time
import random

utils.init_session()

# item 정보 불러오기 pandas
itemData = api.items.showItem()
vannerData : dict = utils.database().firestore_code
vannerKeys = list(vannerData.keys())

if 'vanner_selected_key' not in st.session_state or st.session_state.vanner_selected_key not in vannerKeys:
    st.session_state.vanner_selected_key = random.choice(vannerKeys)
    utils.init_session()

selected_key = st.session_state.vanner_selected_key

code_info : dict = utils.database().firestore_code.get(selected_key)

st.divider()

st.markdown(
    """
    <style>
    .grid-container {
        display: flex;
        flex-direction: column;
        gap: 20px;
        margin-bottom: 40px;
    }
    .grid-top {
        display: flex;
        gap: 20px;
    }
    .grid-left {
        flex: 1;
        background-color: #F8F9FA;
        padding: 40px 30px;
        border-radius: 12px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .grid-right {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .grid-right-top, .grid-right-bottom {
        flex: 1;
        border-radius: 12px;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .grid-right-top {
        background-color: #F4F6F8;
    }
    .grid-right-bottom {
        background-color: #0E3A5B;
        color: white;
    }
    
    @media (max-width: 768px) {
        .grid-top {
            flex-direction: column;
        }
    }
    </style>
    
    <div class="grid-container">
        <!-- 상단 영역 -->
        <div class="grid-top">
            <!-- 좌측 큰 박스 -->
            <div class="grid-left">
                <h2 style='color: #0E3A5B; font-weight: 800; font-family: "Outfit", sans-serif; letter-spacing: -1px; margin-bottom: 20px;'>
                    "아무래도, 역시 AMUREDO"
                </h2>
                <div style="text-align: center; line-height: 1.8; color: #444; font-size:1.05rem; word-break: keep-all;">
                    <b>AMUREDO</b>는 안경을 단순한 패션 아이템이 아닌,<br>
                    당신의 능률을 끌어올릴 <b>최고의 오피스 기어</b>로 정의합니다.<br><br>
                    모니터 앞에서의 치열한 컴퓨터 작업부터 출퇴근 길의 운전까지.<br>
                    당신은 그저 일에만 집중하세요.<br>
                    시야의 편안함은 아무래도가 책임지겠습니다.
                </div>
            </div>
            
            <!-- 우측 위/아래 박스 -->
            <div class="grid-right">
                <div class="grid-right-top">
                    <div>
                        <h4 style="color:#1b5b8d; margin-bottom:10px; font-weight:700;">아무래도 브랜드 철학</h4>
                        <p style="color:#555; font-size:0.95rem; margin:0;">
                            당신의 일상에 스며드는 편안함.<br>화려함보다 본질에 집중합니다.
                        </p>
                    </div>
                </div>
                <div class="grid-right-bottom">
                    <div>
                        <h4 style="color:#ffffff; margin-bottom:10px; font-weight:700; opacity:0.9;">시그니처 컬러 : 딥 네이비</h4>
                        <p style="color:#e2e8f0; font-size:0.95rem; margin:0;">
                            무게감 있는 신뢰와 흔들림 없는 집중력
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### 브랜드 핵심 가치")

# 4개의 기능 카드 (2x2 그리드)
col1, col2 = st.columns(2)

with col1:
    st.html(
        """
        <div class="feature-card">
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
        <div class="feature-card">
            <div class="feature-icon">💎</div>
            <div class="feature-title">Reasonable Price</div>
            <div class="feature-desc">
                불필요한 유통 과정을 줄여 누구나 부담 없이 즐길 수 있는 합리적인 가격을 제안합니다.
            </div>
        </div>
        """
    )

st.write("") # 간격 조정

col3, col4 = st.columns(2)

with col3:
    st.html(
        """
        <div class="feature-card">
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
        <div class="feature-card">
            <div class="feature-icon">✨</div>
            <div class="feature-title">Simple Design</div>
            <div class="feature-desc">
                유행을 타지 않는 미니멀하고 심플한 디자인으로 오래도록 사랑받는 스타일입니다.
            </div>
        </div>
        """
    )

st.divider()

itemList = itemData[itemData['code'] == selected_key]

count_in_card = 0
for i, (index, item) in enumerate(itemList.iterrows()):
    if i % 3 == 0:
        cols = st.columns(spec=3, gap="small", vertical_alignment="top")
    col = cols[i % 3]
    with col.container():
        st.image(str(item['paths'][0]))

        st.markdown(body=f"<div style='font-size: 13px; font-weight: bold;'>{item['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"###### {item['price']:,}원")

        if st.button(
            label='상세보기',
            key=f"loop_item_{index}",
            type='secondary',
            width='stretch'
        ):
            st.session_state.page['item'] = index
            st.session_state.page['page'] = 'pages/7item.py'
            st.switch_page(page="pages/7item.py")

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0; color: #555;'>
            <em>Office Eyewear<br>for Professionals</em>
        </div>
        """,
        unsafe_allow_html=True
    )

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