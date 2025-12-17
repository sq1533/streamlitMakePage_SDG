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

import api
import time

deliveryInfo : dict = utils.database().firestore_vanner.get('deliveryInfo')

utils.init_session()

def imgLoad(path : str):
    if path:
        return st.image(
            image=path,
            width='stretch',
            output_format='JPEG'
        )
    else:
        return st.info(body='not image')

# 상품 키 확인
if not st.session_state.item:
    st.switch_page(page='mainPage.py')
else:
    with st.sidebar:
        st.title(body='amuredo')
        # 회원 로그인 정보 검증
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
                st.info(body='기본 배송지 설정 필요')
                time.sleep(2)
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

    # 홈으로 이동
    goHome = st.button(
        label='HOME',
        type='primary',
        width='content',
        disabled=False
    )
    if goHome:
        st.switch_page(page="mainPage.py")

    itemKey : str = st.session_state.item
    itemInfo = api.items.showItem().loc[itemKey]
    itemStatus : dict = api.items.itemStatus(itemId=itemKey)
    buyAble : bool = not itemStatus.get('enable')
    feedback : dict = itemStatus.get('feedback')
    feedT = feedback.get('text')

    row1, row2 = st.columns(spec=2, gap='small', vertical_alignment='center')
    with row1.container():
        imgLoad(str(itemInfo['paths'][0]))
    with row2.container():
        imgLoad(str(itemInfo['paths'][2]))
    with row1.container():
        imgLoad(str(itemInfo['paths'][1]))
    with row2.container():
        imgLoad(str(itemInfo['paths'][3]))
    
    # 상품 카테고리
    st.markdown(body=f"#### :gray[amuredo > {itemInfo['category']}]")
    # 상품 이름
    st.markdown(f"# {itemInfo['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap='small', vertical_alignment='bottom')
    price.markdown(
        body=f'''
        ##### ~~{int((itemInfo['price']*100/(100-itemInfo['discount'])//100)*100):,}~~
        ### :red[{itemInfo['discount']}%] {itemInfo['price']:,}원 
        '''
        )

    buyBTN = buy.button(
        label='구매하기',
        type='primary',
        disabled=buyAble,
        width='stretch'
    )
    if buyBTN:
        if any(value is not None for value in st.session_state.token.values()):
            st.switch_page(page="pages/5orderPage.py")
        else:
            st.error(body='고객이 확인되지 않습니다.')

    # 상품 상세 정보
    with st.expander(label="상품 세부정보"):
        info, feed = st.tabs(tabs=['info', '후기'])
        with info:
            imgLoad(str(itemInfo['detail']))
            imgLoad(str(itemInfo['package']))
            imgLoad(deliveryInfo.get('path'))
        with feed:
            if feedT.__len__() == 1:
                st.info(body='아직 후기가 없어요...', icon='😪')
            else:
                for i in reversed(feedT[1:]):
                    st.markdown(
                        body=f'''
                        구매 날짜 : {i.split('_')[0]}
                        후기 : {i.split('_')[1]}
                        '''
                        )