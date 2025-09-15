import streamlit as st
import userFunc.userAuth as userAuth
import itemFunc.itemInfo as itemInfo

# 페이지 기본 설정
st.set_page_config(
    page_title="amuredo",
    page_icon=":flying_disc:",
    layout="wide",
    initial_sidebar_state="auto"
)

import utils
from datetime import datetime, timezone, timedelta

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
# 회원 정보
if 'uid' not in st.session_state:
    st.session_state.uid = None

# 상품 주문
if 'item' not in st.session_state:
    st.session_state.item = None

# 주문 상품 상태 변경
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = None

# 페이지 UI 변경 사항
st.markdown(
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
    """,
    unsafe_allow_html=True
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
    buyDisable = not itemInfo.items.itemStatus(itemId=itemID)
    # 이미지 2X2 배치
    row1, row2 = st.columns(spec=2, gap="small", vertical_alignment="center")
    row3, row4 = st.columns(spec=2, gap="small", vertical_alignment="center")
    with row1.container():
        showImage(path=itemIF['paths'][0])
    with row2.container():
        showImage(path=itemIF['paths'][0])
    with row3.container():
        showImage(path=itemIF['paths'][0])
    with row4.container():
        showImage(path=itemIF['paths'][0])
    # 상품 이름
    st.markdown(f"# {itemIF['name']}")
    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : {itemIF['price']} 원 / 배송비 : 무료")
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
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if not st.session_state.user:
            st.error("구매하려면 로그인이 필요합니다.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            if userAuth.guest.showUserEmailCK(uid=st.session_state.uid):
                st.session_state.item = itemID
                st.switch_page(page="pages/5-1orderPage.py")
            else:
                st.error("이메일 인증이 필요합니다. 메일함을 확인해주세요.")


# 페이지 제목
st.title(body='amuredo', anchor='https://amuredo.shop')

# siderbar 정의
with st.sidebar:
    if st.session_state.user:
        logoutB = st.button(
            label="signOut",
            key='signOut',
            type="secondary",
            use_container_width=True
        )
        if logoutB:
            st.session_state.user = None
            st.rerun()

        st.markdown(f'## 환영합니다.')

        if userAuth.guest.showUserEmailCK(uid=st.session_state.uid):
            pass
        else:
            st.warning(body='이메일 인증을 완료해주세요.')

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
                st.switch_page(page="pages/3-3myPageChangePW.py")

            if laterChange:
                userAuth.guest.PWchangeLater(uid=st.session_state.uid, date=nowDay)
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
            st.switch_page(page="pages/4-1myPageOrderList.py")
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
    itemCard = itemInfo.items.itemInfo(itemId=itemKey)['result']
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