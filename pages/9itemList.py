import streamlit as st
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
# 페이지 추가 UI 변경 / columns
st.markdown(
    body="""
    <style>
    @media screen and (max-width: 640px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 10px !important;
        }
        div[data-testid="stColumn"] {
            width: calc(33.333% - 10px) !important; /* 3열 기준 */
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

import api

# 페이지 세션 관리
if 'item' not in st.session_state:
    st.session_state.item = {
        'item' : '',
        'sort' : '',
        'itemKey' : 0
    }

query_page : str|None = st.query_params.get("page", None)

if query_page:
    current_page = query_page
elif st.session_state.item['sort']:
    current_page = st.session_state.item['sort']
else:
    current_page = 'glasses'

if current_page == 'glasses':
    page = {'sort':'glasses'}
    filterOption = ['all', '티타늄 하금테', '티타늄 뿔테', '울템']
elif current_page == 'sunglasses':
    page = {'sort':'sunglasses'}
    filterOption = ['all', '무테', '하프', '뿔테']
elif current_page == 'goggles':
    page = {'sort':'goggles'}
    filterOption = ['all', '무테', '하프', '뿔테']
else:
    page = {'sort':'glasses'}
    filterOption = ['all', '티타늄 하금테', '티타늄 뿔테', '울템']

# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData['sort'] == page.get('sort')]

sortedItems = itemData.sort_index()

# Code 정보 가져오기
code_db : dict = utils.utilsDb().firestore_code

st.title(body=f'AMUREDO {current_page}')
cap, fil = st.columns(spec=[4,1], gap='large', vertical_alignment='bottom')

cap.caption(body='Beyond the basics, comfort in every moment.')
filterValues = fil.selectbox(
    label='필터',
    options=filterOption,
    index=0,
    label_visibility='collapsed',
    width=200
)

st.divider()

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()

if itemData.empty:
    st.info(body='상품 준비중입니다.')
    st.stop()

if filterValues != 'all':
    sortedItems = sortedItems[sortedItems['category'] == filterValues]

grouped_items = sortedItems.groupby('code')

for code, group in grouped_items:
    code_info = code_db.get(str(code))
    st.image(str(code_info['path']), width='stretch')

    with st.container():
        st.html('<div class="mobile-grid-target" style="display:none;"></div>')

        for i, (idx, item) in enumerate(group.iterrows()):
            if i % 3 == 0:
                cols = st.columns(3)
            col = cols[i % 3]

            with col.container():
                # 이미지 표시
                st.image(str(item['paths'][0]))

                model : str = item['name'].split('_')[0]
                color : str = item['name'].split('_')[1]

                # 정보 표시
                st.html(body=f"{model}<br>{color}")

                # 상세보기 버튼
                if st.button(
                    label='상세보기',
                    key=f"loop_item_{idx}",
                    type='secondary',
                    width='stretch'
                ):
                    st.session_state.item['item'] = item['code']
                    st.session_state.item['itemKey'] = i
                    st.switch_page(page="pages/7item.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)