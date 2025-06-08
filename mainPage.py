import streamlit as st
from utils import auth, pyrebase_auth, userInfoDB, logoDB, itemsDB

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="auto"
)

# 세션 관리
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user" not in st.session_state:
    st.session_state.user = False
if "item" not in st.session_state:
    st.session_state.item = False

# 페이지 제목
st.title(body="shop_demo")
# vanner 비디오
st.markdown(
    """
    <style>
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
        width: 80% !important;
        max-width: 800px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# vanner video
@st.cache_data(ttl=None, max_entries=None, show_spinner=True, persist=True)
def cachingVideo(path):
    if path:
        st.video(
            data=path,
            format="video/mp4",
            #start_time=,
            #end_time=,
            loop=True,
            autoplay=True,
            muted=True
        )
    else:
        st.warning("경로가 없습니다.")
cachingVideo(logoDB.document('video').get().to_dict()['path'])

@st.cache_data(ttl=3600) # 1시간 동안 캐시 유지
def get_all_items_as_dicts():
    print("데이터베이스에서 상품 정보를 가져오는 중...")
    items_snapshots = itemsDB.get()
    return [snapshot.to_dict() for snapshot in items_snapshots if snapshot.exists]

# 캐시된 함수를 통해 상품 데이터 로드
items_data = get_all_items_as_dicts()
itemCount = items_data.__len__()
itemCategoly = {i["categoly"] for i in items_data}
itemColor = {i["color"] for i in items_data}
itemEvent = {i["event"] for i in items_data}

@st.cache_data(ttl=None, max_entries=None, show_spinner=True, persist=True)
def cachingImage(path):
    # 경로가 유효한 경우에만 이미지 표시
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

# 사용자 로그인
def signin(id,pw):
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
        user_doc = userInfoDB.document(user["localId"]).get()
        if user_doc.exists:
            if auth.get_user_by_email(email=id).email_verified == False:
                st.error(body="이메일 인증이 안되었어요.")
            else:
                st.session_state.user = user_doc.to_dict()
                st.rerun()
        else:
            st.error("로그인에 성공했으나 Firestore에서 사용자 정보를 찾을 수 없습니다.")
    except Exception:
        st.error(body="Error! 로그인 실패")

# 사용자 로그아웃
def logout():
    st.session_state.user = False
    st.rerun()

# like 상태변화
def likeStatus(likedItem) -> str:
    if not st.session_state.user:
        type="tertiary"
        return type
    else:
        if likedItem in st.session_state.user["like"]:
            type="primary"
        else:
            type="tertiary"
        return type

# liked clicks
def clickedLike(likedItem):
    if not st.session_state.user:
        pass
    else:
        user_doc = userInfoDB.document(st.session_state.user["id"]).get()
        if likedItem in st.session_state.user["like"]:
            st.session_state.user["like"].remove(likedItem)
            user_doc.reference.update({"like": st.session_state.user["like"]})
            st.rerun()
        else:
            st.session_state.user["like"].append(likedItem)
            user_doc.reference.update({"like": st.session_state.user["like"]})
            st.rerun()

# 상품 구매 dialog
@st.dialog("상세 페이지")
def itemInfo(item):
    row1, row2 = st.columns(spec=2, gap="small", vertical_alignment="center")
    row3, row4 = st.columns(spec=2, gap="small", vertical_alignment="center")
    with row1.container():
        cachingImage(item.get("paths")[0])
    with row2.container():
        cachingImage(item.get("paths")[0])
    with row3.container():
        cachingImage(item.get("paths")[0])
    with row4.container():
        cachingImage(item.get("paths")[0])
    # 상품 이름
    st.markdown(f"# {item.get("name")}")
    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : {item.get("price")} 원 / 배송비 : 무료")
    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{item.get('id')}",
        type="primary",
        use_container_width=True
    )
    with st.expander(label="상품 세부정보"):
        st.markdown(body=f"{item.get("detail")}")
    if buyBTN:
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if not st.session_state.user:
            st.error("구매하려면 로그인이 필요합니다.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            st.session_state.item = item.get("id")
            st.switch_page(page="pages/orderPage.py")

# siderbar 정의
with st.sidebar:
    if not st.session_state.user:
        ID = st.text_input(
            label="이메일",
            value=None,
            key="textID",
            type="default",
            placeholder=None
        )
        PW = st.text_input(
            label="비밀번호",
            value=None,
            key="textPW",
            type="password",
            placeholder=None
        )
        login = st.button(
            label="log-IN",
            type="primary",
            use_container_width=True
        )
        signup = st.button(
            label="회원가입",
            type="secondary",
            use_container_width=True
        )
        if login:
            signin(ID,PW)
        if signup:
            st.session_state.signup_step = True
            st.switch_page(page="pages/signup.py")
    else:
        logoutB = st.button(
            label="log-OUT",
            type="secondary",
            use_container_width=True
        )
        if logoutB:
            logout()
        st.markdown(f"## {st.session_state.user['name']} 님! 안녕하세요")
        myinfo, empty, orderList = st.columns(spec=[1,1,1], gap="small", vertical_alignment="center")
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
        if myinfo:
            st.switch_page(page="pages/myPageAccess.py")
        if orderL:
            st.switch_page(page="pages/myPageOrderList.py")
        if not st.session_state.user.get("like"):
            st.markdown("## 내가 좋아한 상품:")
            st.markdown("#### 좋아요한 상품이 없습니다.")
        else:
            st.markdown("## 내가 좋아한 상품:")
            for likes in st.session_state.user["like"]:
                likedItems = [item["name"] for item in items_data if item["id"] == likes]
                for likedItem in likedItems:
                    likeThings = st.button(
                        label=f"### {likedItem}",
                        key=f"liked_{likedItem}",
                        type="primary",
                        use_container_width=True
                    )
                    if likeThings:
                        itemInfo(itemsDB.document(likes).get())

filter_1, filter_2, filter_3, empty = st.columns(spec=4, gap="small", vertical_alignment="top")

colorFilter = filter_1.segmented_control(
    label = "컬러",
    options = itemColor,
    selection_mode = "single",
    default = None,
    key="itemColor",
    label_visibility="visible"
    )

categoryFilter = filter_2.segmented_control(
    label = "카테고리",
    options = itemCategoly,
    selection_mode = "single",
    default = None,
    key="itemCategory",
    label_visibility="visible"
    )

eventFilter = filter_3.segmented_control(
    label = "이벤트",
    options = itemCategoly,
    selection_mode = "single",
    default = None,
    key="itemEvent",
    label_visibility="visible"
    )

count_in_card = 0
line = itemCount//5 + 1

for l in range(line):
    cards = st.columns(spec=5, gap="small", vertical_alignment="top")

for item in items_data:
    if (colorFilter == None or colorFilter == item.get("color")) and (categoryFilter == None or categoryFilter == item.get("categoly")) and (eventFilter == None or eventFilter == item.get("event")):
        with cards[count_in_card].container():
            cachingImage(item.get('path'))
            name, like = st.columns(spec=[3, 1], gap="small", vertical_alignment="center")
            name.markdown(body=f"##### {item.get('name')}")
            likeBTN = like.button(
                label=":heart:",
                key=f"liked_item_{item.get('id')}",
                type=likeStatus(likedItem=item.get('id')),
                use_container_width=True
            )
            if likeBTN:
                clickedLike(likedItem=item.get('id'))
            viewBTN = st.button(
                label="상세보기",
                key=f"loop_item_{item.get('id')}",
                type="primary",
                use_container_width=True
            )
            if viewBTN:
                itemInfo(item=item)
        count_in_card += 1
        if count_in_card == 5:
            count_in_card = 0
        else:
            pass
    else:
        pass