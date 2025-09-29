import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="AMUREDO",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth
import itemFunc.itemInfo as itemInfo
import utils
import time

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'naver':None,
        'kakao':None,
        'gmail':None
    }
# 회원 정보 세션
if 'user' not in st.session_state:
    st.session_state.user = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None

if 'num' not in st.session_state:
    st.session_state.num = 0

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

# 상품 카테고리
category = itemInfo.items.itemCategory()
# 아이템 정보 호출
items = itemInfo.items.itemInfo()

def imgLoad(path : str):
    imageHTML = f"""
        <style>
            .itemsImage {{
                width: 100%;
                height: auto;
                display: block;
            }}
        </style>
        <img src={path} loading="lazy" alt="image sunglasses01" class="itemsImage">
        """
    return imageHTML

# 상품 상세페이지 dialog
@st.dialog(title='상품 상세', width='large')
def showItem(itemID, itemIF):
    buyDisable = not itemInfo.items.itemStatus(itemId=itemID)['enable']

    row1, row2 = st.columns(spec=2, gap='small', vertical_alignment='center')
    with row1.container():
        st.html(body=imgLoad(itemIF['paths'][0]))
    with row2.container():
        st.html(body=imgLoad(itemIF['paths'][1]))
    with row1.container():
        st.html(body=imgLoad(itemIF['paths'][2]))
    with row2.container():
        st.html(body=imgLoad(itemIF['paths'][3]))
    # 상품 이름
    st.markdown(f"# {itemIF['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : ~~{int((itemIF['price']*100/(100-itemIF['discount'])//100)*100)}~~ {itemIF['price']}원( :red[-{itemIF['discount']}%] )")

    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{itemID}",
        type="primary",
        disabled=buyDisable,
        use_container_width=True
    )
    with st.expander(label="상품 세부정보"):
        st.html(body=f"{itemIF['detail']}")

    if buyBTN:
        if any(value is not None for value in st.session_state.token.values()):
            st.session_state.item = itemID
            st.switch_page(page="pages/5orderPage.py")
        else:
            st.error(body='고객이 확인되지 않습니다.')

# 상단 vanner
st.html(
    body=f"""
    <style>
        .fullscreen-gif {{
            width: 100%;
            height: auto;
            aspect-ratio: 21 / 9;
            object-fit: cover;
        }}
    </style>
    <img src="{utils.database().firestore_vanner.to_dict()['path']}" class="fullscreen-gif">
    """
)

# siderbar 정의
with st.sidebar:
    st.title(body='amuredo')
    if any(value is not None for value in st.session_state.token.values()):
        st.session_state.user = userAuth.guest.showUserInfo(token=st.session_state.token)
        logoutB = st.button(
            label="signOut",
            key='signOut',
            type="secondary",
            use_container_width=True
        )
        if logoutB:
            st.session_state.clear()
            st.rerun()

        # 소셜 고객 배송정보 확인
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


    colorFilter = st.segmented_control(
        label = "컬러",
        options = category['color'],
        selection_mode = "single",
        default = None,
        key="itemColor",
        label_visibility="visible"
        )

    seriesFilter = st.segmented_control(
        label = "시리즈",
        options = category['series'],
        selection_mode = "single",
        default = None,
        key="itemSeries",
        label_visibility="visible"
        )

count_in_card = 0
line = category['key'].__len__()//4 + 1

# 아이템에 따른 행 갯수 수정
for l in range(line):
    cards = st.columns(spec=4, gap="small", vertical_alignment="top")

# 아이템 4열 배치
for itemKey in category['key']:
    itemCard = items[itemKey]
    if (colorFilter == None or colorFilter in itemCard['color']) and (seriesFilter == None or seriesFilter in itemCard['series']):
        with cards[count_in_card].container():
            feedback = itemInfo.items.itemStatus(itemId=itemKey)['feedback']

            st.html(body=imgLoad(itemCard['paths'][0]))

            st.markdown(body=f"###### {itemCard['name']}")
            st.markdown(body=f':heart: {feedback['point']}%')

            viewBTN = st.button(
                label="상세보기",
                key=f"loop_item_{itemKey}",
                type="primary",
                use_container_width=True
            )
            if viewBTN:
                showItem(itemID=itemKey, itemIF=itemCard)

        count_in_card += 1
        if count_in_card == 4:
            count_in_card = 0
        else:
            pass
    else:
        pass

st.divider()

policy, cookies, empty = st.columns(spec=[1,1,3], gap='small', vertical_alignment='center')

policyB = policy.button(
    label='개인정보 처리방침',
    key='policy',
    type='tertiary',
    use_container_width=False
)

cookiesB = cookies.button(
    label='쿠키 정책',
    key='cookiesPolicy',
    type='tertiary',
    use_container_width=False
)

if policyB:
    st.switch_page(page='pages/0policy.py')

if cookiesB:
    st.switch_page(page='pages/0cookies.py')

st.html(body=utils.database().infoAdmin)