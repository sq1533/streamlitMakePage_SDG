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
import time
import pandas as pd

utils.init_session()

query_page = st.query_params.get("page", None)

if query_page:
    current_page = query_page
elif st.session_state.page:
    current_page = st.session_state.page
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

# siderbar 정의
with st.sidebar:
    utils.set_sidebarLogo()
    # 회원 로그인 상태 확인
    if any(value is not None for value in st.session_state.token.values()):
        logoutB = st.button(
            label='sign_out',
            type='secondary',
            width='stretch'
        )
        if logoutB:
            st.session_state.clear()
            st.rerun()

        if st.session_state.user.get('address'):
            pass
        else:
            st.toast("기본 배송지 설정 필요", icon="⚠️")
            time.sleep(0.7)
            st.switch_page(page='pages/1signIN_address.py')

        myinfo, orderList = st.columns(spec=2, gap="small", vertical_alignment="center")

        myinfo = myinfo.button(
            label='마이페이지',
            type='tertiary',
            width='stretch'
        )
        orderL = orderList.button(
            label='주문내역',
            type='tertiary',
            width='stretch'
        )

        # 마이페이지
        if myinfo:
            st.switch_page(page="pages/3myPage.py")
        # 주문 내역 페이지
        if orderL:
            st.switch_page(page="pages/3myPage_orderList.py")
    else:
        signIn = st.button(
            label='로그인 / 회원가입',
            type='primary',
            width='stretch'
        )
        if signIn:
            st.switch_page(page="pages/1signIN.py")

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
                    type='primary',
                    width='stretch'
                ):
                    st.session_state.item = idx
                    st.query_params["item_id"] = idx
                    st.switch_page(page="pages/7item.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)