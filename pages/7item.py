import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time

# 파라미터 접근 확인
if "item_id" in st.query_params:
    st.session_state.page['item'] = st.query_params["item_id"]

# 페이지 접근 검증
if st.session_state.page['item'] == '':
    st.switch_page(page='mainPage.py')

# 페이지 시작
st.session_state.page['page'] = 'pages/7item.py'
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

itemKey : str = st.session_state.page['item']
itemInfo = api.items.showItem().loc[itemKey]
itemStatus : dict = api.items.itemStatus(itemId=itemKey)
buyAble : bool = not itemStatus.get('enable')
feedback : dict = itemStatus.get('feedback')
feedCount : int = feedback.get('count', 0)
feedPoint : int = feedback.get('point', 0)
feedAvg : int = int((feedPoint / feedCount) * 100) if feedCount > 0 else 0
feedText : list = feedback.get('text')

st.html("""
<style>
[data-testid="stCode"] button {
    visibility: visible !important;
    opacity: 1 !important;
    background-color: #ffffff !important;
    color: #000000 !important;
    border: none !important;
    position: absolute !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
    cursor: pointer !important;
    pointer-events: auto !important; /* 클릭 이벤트 활성화 */
}

[data-testid="stCode"] button svg {
    visibility: visible !important;
    opacity: 1 !important;
}
</style>
""")

with st.container(horizontal=True):
    st.markdown(body=f"#### :gray[amuredo > {itemInfo['category']}]")
    st.space(size='stretch')
    with st.popover(label='공유하기'):
        st.code(f"https://amuredo.shop/item?item_id={itemKey}", language="text")

st.markdown(f"# {itemInfo['name']}")
price, buy = st.columns(spec=2, gap='small', vertical_alignment='bottom')

price.markdown(body=f"### {itemInfo['price']:,}원")

buy_naver, buy_kakao = buy.columns(2)

with buy_naver:
    st.link_button(
        label='네이버 스토어 구매',
        url=f'https://smartstore.naver.com/amuredo?item_id={itemKey}', # 임시 목적지 URL
        type='secondary',
        use_container_width=True
    )

with buy_kakao:
    st.link_button(
        label='카카오 쇼핑 구매',
        url=f'https://store.kakao.com/amuredo?item_id={itemKey}', # 임시 목적지 URL
        type='secondary',
        use_container_width=True
    )

lensOption = st.selectbox(
    label='lensOptionSelect',
    options=['변색렌즈_브라운(40,000원)','변색렌즈_그레이(40,000원)','편광렌즈(50,000원)','UV차단렌즈(30,000원)'],
    index=None,
    key='lens',
    placeholder='렌즈 옵션 변경',
    label_visibility='collapsed',
    width='stretch'
)
if lensOption:
    st.session_state.page['lens'] = lensOption
else:
    pass

design, info, feed = st.tabs(tabs=['design', 'information', 'review'])

with design:
    st.image(str(itemInfo['paths'][1]))

with info:
    st.image(str(itemInfo['detail']))

with feed:
    st.markdown(body=f"####  :heart: {feedAvg}%")
    if feedText.__len__() == 1:
        st.info(body='아직 후기가 없어요...', icon='😪')
    else:
        for i in reversed(feedText[1:]):
            parts = i.split('_', 1)
            if len(parts) < 2:
                continue

            date = parts[0]
            content = parts[1]

            st.markdown(
                f"""
                **📅 {date}**
                > {content}
                """
            )
            st.divider()