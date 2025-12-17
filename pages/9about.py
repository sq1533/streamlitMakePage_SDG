import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.database().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)

# 페이지 UI 변경 사항
utils.set_page_ui()
# 페이지 UI 변경 사항
st.html(
    """
    <style>
    .feature-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        height: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 2em;
        margin-bottom: 10px;
    }
    .feature-title {
        font-weight: bold;
        font-size: 1.2em;
        margin-bottom: 10px;
        color: #333;
    }
    .feature-desc {
        color: #666;
        font-size: 0.9em;
        line-height: 1.5;
    }
    h3 {
        text-align: center;
        margin-bottom: 40px;
    }
    </style>
    """
)

# 홈으로 이동
goHome = st.button(
    label='HOME',
    type='primary',
    width='content',
    disabled=False
)
if goHome:
    st.switch_page(page="mainPage.py")

st.title(body='AMUREDO')
st.caption(body='Beyond the basics, comfort in every moment.')

st.divider()

st.markdown("### 브랜드 철학")
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 50px; line-height: 1.8; color: #444;">
        <b>AMUREDO</b>는 당신의 일상에 자연스럽게 스며드는 편안함을 추구합니다.<br>
        화려한 장식보다는 본질에 집중하며, 언제 어디서나 부담 없이 착용할 수 있는 안경을 만듭니다.<br>
        우리는 안경이 아닌, 당신의 하루를 디자인합니다.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("### 핵심 가치")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.html(
        """
        <div class="feature-card">
            <div class="feature-icon">☁️</div>
            <div class="feature-title">Comfortable Fit</div>
            <div class="feature-desc">
                마치 쓰지 않은 듯한 편안함.<br>
                인체 공학적 패턴으로<br>
                최상의 착용감을 선사합니다.
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
                불필요한 유통 과정을 줄여<br>
                누구나 부담 없이 즐길 수 있는<br>
                합리적인 가격을 제안합니다.
            </div>
        </div>
        """
    )

with col3:
    st.html(
        """
        <div class="feature-card">
            <div class="feature-icon">🪶</div>
            <div class="feature-title">Light Weight</div>
            <div class="feature-desc">
                하루 종일 써도 피로하지 않은<br>
                가벼운 소재를 사용하여<br>
                활동성을 극대화했습니다.
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
                유행을 타지 않는<br>
                미니멀하고 심플한 디자인으로<br>
                오래도록 사랑받는 스타일입니다.
            </div>
        </div>
        """
    )

st.divider()
st.html(body=utils.database().infoAdmin)