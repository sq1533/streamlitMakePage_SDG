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

deliveryInfo : dict = utils.utilsDb().firestore_vanner.get('deliveryInfo')

utils.init_session()

if "item_id" in st.query_params:
    st.session_state.item = st.query_params["item_id"]

# 상품 키 확인
if not st.session_state.item:
    st.switch_page(page='mainPage.py')
else:

    with st.sidebar:
        st.page_link(
            page='mainPage.py',
            label='AMUREDO'
        )

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

    itemKey : str = st.session_state.item
    itemInfo = api.items.showItem().loc[itemKey]
    itemStatus : dict = api.items.itemStatus(itemId=itemKey)
    buyAble : bool = not itemStatus.get('enable')
    feedback : dict = itemStatus.get('feedback')
    feedCount : int = feedback.get('count', 0)
    feedPoint : int = feedback.get('point', 0)
    feedAvg : int = int((feedPoint / feedCount) * 100) if feedCount > 0 else 0
    feedText : list = feedback.get('text')
        
    # 상품 카테고리
    st.markdown(body=f"#### :gray[amuredo > {itemInfo['category']}]")
    # 상품 이름
    st.markdown(f"# {itemInfo['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap='small', vertical_alignment='bottom')

    price.markdown(body=f"### {itemInfo['price']:,}원")

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

    info, feed = st.tabs(tabs=['detail', 'review'])

    with info:
        img_detail = utils.load_and_optimize_from_url(str(itemInfo['detail']))
        if img_detail:
            st.image(img_detail, output_format='WEBP')
        else:
            st.image(image=str(itemInfo['detail']), output_format='JPEG')
        
        img_delivery = utils.load_and_optimize_from_url(str(deliveryInfo.get('path')))
        if img_delivery:
            st.image(img_delivery, output_format='WEBP')
        else:
            st.image(image=str(deliveryInfo.get('path')), output_format='JPEG')
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