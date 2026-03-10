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

import api

# 페이지 세션 관리
if 'item' not in st.session_state:
    st.session_state.item = {
        'item' : '',
        'itemKey' : 0
    }

# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData['sort'] == 'sunglasses']

sortedItems = itemData.sort_index()

# Code 정보 가져오기
code_db : dict = utils.utilsDb().firestore_code

st.title(body='AMUREDO sunglasses')
st.caption(body='Beyond the basics, comfort in every moment.')

st.divider()

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()

if itemData.empty:
    st.info(body='상품 준비중입니다.')
    st.stop()

grouped_items = sortedItems.groupby('code')

for row_index, (code, group) in enumerate(grouped_items):
    code_info = code_db.get(str(code))
    col1, col2 = st.columns(spec=2, gap='small', vertical_alignment='top')

    item = group.iloc[0]
    idx = item.name

    if row_index % 2 == 0:
        code_col, item_col = col1, col2
    else:
        item_col, code_col = col1, col2
        
    with code_col:
        st.image(str(code_info['path']), width='stretch')

    with item_col:        
        # 이미지 표시
        st.image(str(item['paths'][0]), width='stretch')
        model : str = item['name'].split('_')[0]
        color : str = item['color']

        st.space(size='stretch')

        # 정보 표시 (폰트 크기 및 색상 수정 가능)
        st.html(
        body=f"""
        <div style='font-size: 1.5rem; line-height: 1.5; color: #0e3a5b;'>
            <b>{model}</b><br>
            <span style='font-size: 1.2rem; color: #555;'>{color}</span>
        </div>
        """)

        st.space(size='stretch')

        # 상세보기 버튼
        if st.button(
            label='상세보기',
            key=f"loop_item_{idx}",
            type='secondary',
            width='stretch'
        ):
            st.session_state.item['item'] = item['code']
            st.session_state.item['itemKey'] = 0
            st.switch_page(page="pages/7item.py")
    st.divider()

st.html(body=utils.utilsDb().infoAdmin)