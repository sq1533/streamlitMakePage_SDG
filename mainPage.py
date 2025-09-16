import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="amuredo",
    page_icon=":flying_disc:",
    layout="wide",
    initial_sidebar_state="auto"
)

import userFunc.userAuth as userAuth
import itemFunc.itemInfo as itemInfo
from datetime import datetime, timezone, timedelta

# 회원 로그인 구분
if 'token' not in st.session_state:
    st.session_state.token = {
        'firebase':None,
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

# 페이지 UI 변경 사항
st.html(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
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

# 이미지 고정 설정
def showImage(path : str):
    try:
        st.image(
            image=path,
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )
    except Exception as e:
        st.warning(f'이미지 호출 실패 {e}')

# 상품 상세페이지 dialog
@st.dialog(title='상품 상세', width='large')
def showItem(itemID, itemIF):
    buyDisable = not itemInfo.items.itemStatus(itemId=itemID)['enable']
    # 이미지 2X2 배치
    row1, row2 = st.columns(spec=2, gap="small", vertical_alignment="center")
    row3, row4 = st.columns(spec=2, gap="small", vertical_alignment="center")
    with row1.container():
        showImage(path=itemIF['paths'][0])
    with row2.container():
        showImage(path=itemIF['paths'][1])
    with row3.container():
        showImage(path=itemIF['paths'][2])
    with row4.container():
        showImage(path=itemIF['paths'][3])

    # 상품 이름
    st.markdown(f"# {itemIF['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : {itemIF['price']} 원")

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
        if st.session_state.token and userAuth.guest.showEmailVerified(token=st.session_state.token):
            st.session_state.item = itemID
            st.switch_page(page="pages/5orderPage.py")
        else:
            st.error(body='고객이 확인되지 않습니다.')

# 페이지 제목
st.title(body='amuredo', anchor='https://amuredo.shop')

# siderbar 정의
with st.sidebar:
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

        st.markdown(f'## 환영합니다.')

        if st.session_state.token['firebase']:
            if userAuth.guest.showEmailVerified(token=st.session_state.token):
                pass
            else:
                st.warning(body='이메일 인증을 완료해주세요.')
        else:
            pass

        createPW = st.session_state.user.get('createPW')
        now = datetime.now(timezone.utc) + timedelta(hours=9)
        nowDay = now.strftime('%Y-%m-%d')

        orderDay_d = datetime.strptime(createPW, '%Y-%m-%d').date()
        nowDay_d = datetime.strptime(nowDay, '%Y-%m-%d').date()
        elapsed = (nowDay_d - orderDay_d).days

        if elapsed > 90:
            st.warning(body='비밀번호를 변경한지 90일이 지났습니다. 비밀번호를 변경해주세요.')

            YES, NO = st.columns(spec=2, gap="small", vertical_alignment="center")

            pwChange = YES.button(
                label="변경하기",
                type="tertiary",
                key="pwChange",
                use_container_width=True
            )
            laterChange = NO.button(
                label="나중에..",
                type="secondary",
                key="laterChange",
                use_container_width=True
            )
            if pwChange:
                st.switch_page(page="pages/3myPage_changePW.py")

            if laterChange:
                userAuth.guest.PWchangeLater(token=st.session_state.token, date=nowDay)
                st.session_state.user['createPW'] = nowDay
                st.rerun()
            else:
                pass

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
            st.switch_page(page="pages/3myPage_access.py")
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

    # 상품 카테고리
    category = itemInfo.items.itemCategory()

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
    itemCard = itemInfo.items.itemInfo()[itemKey]
    if (colorFilter == None or colorFilter in itemCard['color']) and (seriesFilter == None or seriesFilter in itemCard['series']):
        with cards[count_in_card].container():
            showImage(itemCard['paths'][0])
            st.markdown(body=f"###### {itemCard['name']}")
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
st.write('통신판매업을 위한 정보 기입')