import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
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
itemData['sales'] = itemData.index.map(
    lambda x: all_status.get(x, {}).get('sales', 0)
)

sortedItems = itemData.sort_index()

# siderbar 정의
with st.sidebar:
    # 홈으로 이동 (네이티브 링크 사용)
    st.page_link(
        page='mainPage.py',
        label='amuredo'
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

count_in_card = 0
line = itemID.__len__()//3 + 1

# 아이템에 따른 행 갯수 수정
for l in range(line):
    cards = st.columns(spec=3, gap="small", vertical_alignment="top")

# 아이템 3열 배치
for index, item in sortedItems.iterrows():
    with cards[count_in_card].container():
        itemStatus : dict = api.items.itemStatus(itemId=index)
        feedback : dict = itemStatus.get('feedback')

        st.image(
            image=str(item['paths'][0]),
            output_format='JPEG'
        )

        st.markdown(body=f"###### {item['name']} :heart: {feedback.get('point', 0)}")
        st.markdown(f"###### {item['price']:,}원")

        viewBTN = st.button(
            label='상세보기',
            key=f"loop_item_{index}",
            type='primary',
            width='stretch'
        )
        if viewBTN:
            st.session_state.item = index
            st.switch_page(page="pages/7item.py")

    count_in_card += 1
    if count_in_card == 3:
        count_in_card = 0
    else:
        pass

st.divider()

st.html(body=utils.utilsDb().infoAdmin)