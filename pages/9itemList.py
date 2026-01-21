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

if st.session_state.page == 'glasses':
    page = {'sort':'glasses'}
elif st.session_state.page == 'sunglasses':
    page = {'sort':'sunglasses'}
elif st.session_state.page == 'sporty':
    page = {'category':'sporty'}
elif st.session_state.page == 'new':
    page = {'event':'new'}
else:
    st.switch_page(page='mainPage.py')

index : str = list(page.keys())[0]

# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData[index] == page.get(index)]

itemID = itemData.index.tolist()

all_status = api.items.getAllItemStatus()

sortedItems = itemData.sort_index()

# siderbar 정의
with st.sidebar:
    st.page_link(
        page='mainPage.py',
        label='AMUREDO'
    )

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

# 아이템 3열 배치
for i, (index, item) in enumerate(sortedItems.iterrows()):
    if i % 3 == 0:
        cols = st.columns(3)
    col = cols[i % 3]
    with col.container():
        # 개별 API 호출 제거 -> 일괄 조회된 데이터(all_status) 사용
        itemStatus = all_status.get(index, {})
        feedback = itemStatus.get('feedback', {})
        
        # 이미지 표시
        if item['paths']:
            thumb_img = utils.load_and_optimize_from_url(str(item['paths'][0]), quality=80)
            if thumb_img:
                st.image(thumb_img, output_format='WEBP')
            else:
                st.image(image=str(item['paths'][0]), output_format='JPEG')

        # 정보 표시
        st.markdown(body=f"###### {item['name']} :heart: {feedback.get('point', 0)}")
        st.markdown(f"###### {item['price']:,}원")

        # 상세보기 버튼
        if st.button(
            label='상세보기',
            key=f"loop_item_{index}",
            type='primary',
            width='stretch'
        ):
            st.session_state.item = index
            st.switch_page(page="pages/7item.py")

st.divider()

st.html(body=utils.utilsDb().infoAdmin)