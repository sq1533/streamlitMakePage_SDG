import streamlit as st
import utils
from datetime import datetime, timezone, timedelta
from streamlit_js_eval import streamlit_js_eval

# 페이지 기본 설정
st.set_page_config(
    page_title="amuredo",
    page_icon=":flying_disc:",
    layout="wide",
    initial_sidebar_state="auto"
)

# 페이지 진입 초기 너비 감지
screen_width = streamlit_js_eval(js_expressions='screen.width', key='screen_width_key')

# items 데이터 호출 list > key : values
itemsInfoList = utils.database().pyrebase_db_items.get().each()
itemsInfoDict = utils.database().pyrebase_db_items.get().val()

# 회원 가입 구분
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False

# 회원 로그인 구분
if "user" not in st.session_state:
    st.session_state.user = None

# 회원 허용 유무
if "userAllow" not in st.session_state:
    st.session_state.userAllow = False

# 상품 구매 페이지
if "item" not in st.session_state:
    st.session_state.item = False

# 페이지 UI 변경 사항
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    video::-webkit-media-controls {
        display: none !important;
    }
    video {
        width: 100% !important;
        aspect-ratio: 20 / 9;
        object-fit: fill;
    }
    button[data-testid="stBaseButton-elementToolbar"][aria-label="Fullscreen"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 75% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# UX function
# 이미지 고정 설정
def showImage(path : str):
    if path:
        st.image(
            image=path,
            caption=None,
            use_container_width=True,
            clamp=False,
            output_format="auto"
            )
    else:
        st.warning("이미지 경로가 없습니다.")

# 상품 상세페이지 dialog
@st.dialog("상세 페이지")
def showItem(item): # item == itemId로 검색
    itemInfo = itemsInfoDict[item]
    # 이미지 2X2 배치
    row1, row2 = st.columns(spec=2, gap="small", vertical_alignment="center")
    row3, row4 = st.columns(spec=2, gap="small", vertical_alignment="center")
    with row1.container():
        showImage(path=itemInfo['paths'][0])
    with row2.container():
        showImage(path=itemInfo['paths'][0])
    with row3.container():
        showImage(path=itemInfo['paths'][0])
    with row4.container():
        showImage(path=itemInfo['paths'][0])
    # 상품 이름
    st.markdown(f"# {itemInfo['name']}")
    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : {itemInfo['price']} 원 / 배송비 : 무료")
    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{item}",
        type="primary",
        use_container_width=True
    )
    with st.expander(label="상품 세부정보"):
        st.markdown(body=f"{itemInfo['detail']}")
    if buyBTN:
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if not st.session_state.user:
            st.error("구매하려면 로그인이 필요합니다.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            if not st.session_state.userAllow:
                st.error("이메일 인증이 필요합니다. 메일함을 확인해주세요.")
            else:
                st.session_state.item = item
                st.switch_page(page="pages/orderPage.py")

# 메인 페이지
# 페이지 제목
st.html(
    body="<h1 style='font-family:Oswald, sans-serif; text-align:center'>AMU:)redo</h1>"
    )

# siderbar 정의
with st.sidebar:
    if st.session_state.user:
        logoutB = st.button(
            label="log-OUT",
            type="secondary",
            use_container_width=True
        )
        if logoutB:
            st.session_state.user = None
            st.rerun()

        # 이메일 검증 유무 확인
        emailVer = utils.database().pyrebase_auth.get_account_info(st.session_state.user['idToken'])
        email_verified = emailVer['users'][0]['emailVerified']
        if email_verified:
            st.session_state.userAllow = True
        else:
            pass

        st.markdown(f'## 환영합니다.')
        myinfo, orderList = st.columns(spec=2, gap="small", vertical_alignment="center")
        myinfo = myinfo.button(
            label="마이페이지",
            type="tertiary",
            key="myPage",
            use_container_width=True
        )
        orderL = orderList.button(
            label="주문내역",
            type="tertiary",
            key="orderList",
            use_container_width=True
        )

        # 회원 비밀번호 생성기간 확인
        userInfo = utils.guest.showUserInfo(uid=st.session_state.user['localId'], token=st.session_state.user['idToken'])
        if userInfo['allow']:
            createPW = userInfo['result'].get('createPW')
            now = datetime.now(timezone.utc) + timedelta(hours=9)
            nowDay = now.strftime('%Y-%m-%d')
            orderDay_d = datetime.strptime(createPW, '%Y-%m-%d').date()
            nowDay_d = datetime.strptime(nowDay, '%Y-%m-%d').date()
            elapsed = (nowDay_d - orderDay_d).days
            if elapsed > 90:
                st.warning(
                    body='비밀번호를 변경한지 90일이 지났습니다. 비밀번호를 변경해주세요.'
                    )
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
                    st.switch_page(page="pages/myPageChangePW.py")
                if laterChange:
                    utils.guest.PWlaterChange(uid=st.session_state.user['localId'], date=now.strftime("%Y-%m-%d"))
                    st.rerun()
            else:
                pass
        else:
            st.warning(
                body=userInfo['result']
            )

        # 마이페이지
        if myinfo:
            st.switch_page(page="pages/myPageAccess.py")

        # 주문 내역 페이지
        if orderL:
            st.switch_page(page="pages/myPageOrderList.py")
    else:
        ID = st.text_input(
            label="email",
            value=None,
            key="textID",
            type="default",
            placeholder=None
        )
        PW = st.text_input(
            label="password",
            value=None,
            key="textPW",
            type="password",
            placeholder=None
        )
        login = st.button(
            label="signIN",
            type="primary",
            use_container_width=True
        )
        signup = st.button(
            label="회원가입",
            type="secondary",
            use_container_width=True
        )
        if (ID and PW) or login:
            goSignIn = utils.guest.signIN(id=ID, pw=PW)
            if goSignIn['allow']:
                st.session_state.user = goSignIn['result']
                st.rerun()
            else:
                st.error(
                    body='로그인 실패, 계정정보를 확인해주세요.'
                )
        if signup:
            st.session_state.signup_step = True
            st.switch_page(page="pages/signup.py")

    # 상품 카테고리
    itemColor = list(set([item.val()['color'] for item in itemsInfoList]))
    itemCategory = list(set([item.val()['category'] for item in itemsInfoList]))
    itemEvent = list(set([item.val()['event'] for item in itemsInfoList]))

    colorFilter = st.segmented_control(
        label = "컬러",
        options = itemColor,
        selection_mode = "single",
        default = None,
        key="itemColor",
        label_visibility="visible"
        )

    categoryFilter = st.segmented_control(
        label = "시리즈",
        options = itemCategory,
        selection_mode = "single",
        default = None,
        key="itemCategory",
        label_visibility="visible"
        )

    eventFilter = st.segmented_control(
        label = "이벤트",
        options = itemEvent,
        selection_mode = "single",
        default = None,
        key="itemEvent",
        label_visibility="visible"
        )

if screen_width >= 700:
    lineCount = 4
else:
    lineCount = 2

count_in_card = 0
line = itemsInfoList.__len__()//lineCount + 1

for l in range(line):
    cards = st.columns(spec=lineCount, gap="small", vertical_alignment="top")

for item in utils.items.itemsIdList():
    if (colorFilter == None or colorFilter == itemsInfoDict[item]['color']) and (categoryFilter == None or categoryFilter == itemsInfoDict[item]['category']) and (eventFilter == None or eventFilter == itemsInfoDict[item]['event']):
        with cards[count_in_card].container():
            showImage(itemsInfoDict[item]['paths'][0])
            st.markdown(body=f"##### {itemsInfoDict[item]['name']}")
            viewBTN = st.button(
                label="상세보기",
                key=f"loop_item_{item}",
                type="primary",
                use_container_width=True
            )
            if viewBTN:
                showItem(item=item)
        count_in_card += 1
        if count_in_card == lineCount:
            count_in_card = 0
        else:
            pass
    else:
        pass