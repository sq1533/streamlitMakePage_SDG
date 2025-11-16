import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=':a:',
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
st.html(
    """
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    video::-webkit-media-controls {
        display: none !important;
    }
    video {
        width: 100% !important;
        aspect-ratio: 20 / 9;
        object-fit: fill;
    }
    </style>
    """
)

import api
import time

# 회원 토큰 및 정보 세선
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
if 'user' not in st.session_state:
    st.session_state.user = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None

itemIF : dict = api.items.showItem().get(st.session_state.item)

def imgLoad(path : str):
    if path:
        return st.image(
            image=path,
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
                label="signOut",
                key='signOut',
                type="secondary",
                use_container_width=True
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
                key='myPage',
                type='tertiary',
                use_container_width=True
            )
            orderL = orderList.button(
                label='주문내역',
                key='orderList',
                type='tertiary',
                use_container_width=True
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
                key='signUPIN',
                type='primary',
                use_container_width=True
            )
            if signIn:
                st.switch_page(page="pages/1signIN.py")

    itemID : str = st.session_state.item

    itemStatus : dict = api.items.itemStatus(itemId=itemID)
    buyDisable = not itemStatus.get('enable')
    feedT = itemStatus.get('feedback').get('text')

    row1, row2 = st.columns(spec=2, gap='small', vertical_alignment='center')
    with row1.container():
        imgLoad(str(itemIF.paths[0]))
    with row2.container():
        imgLoad(str(itemIF.paths[1]))
    with row1.container():
        imgLoad(str(itemIF.paths[2]))
    with row2.container():
        imgLoad(str(itemIF.paths[3]))
    # 상품 이름
    st.markdown(f"# {itemIF.name}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : ~~{int((itemIF.price*100/(100-itemIF.discount)//100)*100)}~~:red[-{itemIF.discount}%] {itemIF.price}원")

    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{itemID}",
        type="primary",
        disabled=buyDisable,
        use_container_width=True
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
            imgLoad(str(itemIF.detail))
        with feed:
            if feedT.__len__() == 1:
                st.info(body='아직 후기가 없어요...', icon='😪')
            else:
                for i in reversed(feedT[1:]):
                    st.markdown(body=i.keys())
                    st.markdown(body=i.values())