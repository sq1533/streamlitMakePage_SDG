import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 세션 확인
utils.init_session()
# 페이지 UI 변경 사항
utils.set_page_ui()

import api
import time
import pandas as pd

query_page : str|None = st.query_params.get("page", None)
st.session_state.page['page'] = 'pages/9itemList.py'

if query_page:
    current_page = query_page
elif st.session_state.page['sort']:
    current_page = st.session_state.page['sort']
else:
    current_page = 'glasses'

if current_page == 'glasses':
    page = {'sort':'glasses'}
elif current_page == 'sunglasses':
    page = {'sort':'sunglasses'}
elif current_page == 'sporty':
    page = {'category':'sporty'}
elif current_page == 'new':
    page = {'event':'new'}
elif current_page == 'best':
    page = {'event':'best'}
else:
    page = {'sort':'glasses'}

index : str = list(page.keys())[0]

# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData[index] == page.get(index)]

sortedItems = itemData.sort_index()

# Code 정보 가져오기
code_db : dict = utils.utilsDb().firestore_code

st.title(body=f'AMUREDO {current_page}')
st.caption(body='Beyond the basics, comfort in every moment.')

st.divider()

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

if itemData.empty:
    st.info(body='상품 준비중입니다.')
    st.stop()

grouped_items = sortedItems.groupby('code')

for code, group in grouped_items:
    
    code_info = code_db.get(str(code))
    st.image(str(code_info['path']), width='stretch')

    # 2. 아이템 3열 배치
    # 한번만 Marker를 생성하기 위해 컨테이너로 감쌉니다.
    with st.container():
        st.html('<div class="mobile-grid-target" style="display:none;"></div>')
        for i, (idx, item) in enumerate(group.iterrows()):
            if i % 3 == 0:
                cols = st.columns(3)
            
            col = cols[i % 3]
            with col.container():
                
                # 이미지 표시
                st.image(str(item['paths'][0]))
    
                # 정보 표시
                st.markdown(body=f"<div style='font-size: 13px; font-weight: bold;'>{item['name']}</div>", unsafe_allow_html=True)
                st.markdown(f"###### {item['price']:,}원")
    
                # 상세보기 버튼
                if st.button(
                    label='상세보기',
                    key=f"loop_item_{idx}",
                    type='secondary',
                    width='stretch'
                ):
                    st.session_state.page['item'] = idx
                    st.session_state.page['page'] = 'pages/7item.py'
                    st.switch_page(page="pages/7item.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)