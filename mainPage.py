import streamlit as st
from utils import db, pyrebase_auth, logo_data, itemsDB

# 페이지 기본 설정
st.set_page_config(
    page_title="shop_demo",
    page_icon=":shark:",
    layout="wide",
    initial_sidebar_state="expanded"
)
# 페이지 로고
st.logo(image=logo_data.get("path"), size="large")
# 페이지 제목
st.title(body="shop_demo")

# st.video()

# 세션 관리
if "signup_step" not in st.session_state:
    st.session_state.signup_step = False
if "user" not in st.session_state:
    st.session_state.user = False
if "item" not in st.session_state:
    st.session_state.item = False

@st.cache_data(ttl=3600) # 1시간 동안 캐시 유지
def get_all_items_as_dicts():
    """Firestore에서 모든 상품 정보를 가져와 딕셔너리 리스트로 반환합니다."""
    print("데이터베이스에서 상품 정보를 가져오는 중...") # 캐시 동작 확인용 로그
    items_snapshots = itemsDB.get()
    return [snapshot.to_dict() for snapshot in items_snapshots if snapshot.exists]

# 캐시된 함수를 통해 상품 데이터 로드
items_data = get_all_items_as_dicts()

# 사용자 로그인
def signin(id,pw):
    userInfoDB = db.collection('userInfo')
    try:
        user = pyrebase_auth.sign_in_with_email_and_password(email=id, password=pw)
        user_doc = userInfoDB.document(user["localId"]).get()
        if user_doc.exists:
            st.session_state.user = user_doc.to_dict()
            print(f"사용자 로그인 성공.")
            st.rerun()
        else:
            st.error("로그인에 성공했으나 Firestore에서 사용자 정보를 찾을 수 없습니다.")
            st.session_state.user = False
    except Exception as e:
        print(f"로그인 실패: {e}")
        st.session_state.user = False
        st.error(body="로그인 실패,\n\n\n아이디 또는 비밀번호를 확인해주세요.")

# 사용자 로그아웃
def logout():
    st.session_state.user = False
    st.rerun()

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
            type="primary",
            use_container_width=True
        )
        if logoutB:
            logout()
        st.write(f"환영합니다, {st.session_state.user["name"]} 고객님!")
        if not st.session_state.user.get("like"):
            st.write("좋아요한 상품이 없습니다.")
        else:
            st.write("내가 좋아한 상품:")
            for liked_item_id in st.session_state.user["like"]:
                liked_item_doc = itemsDB.document(liked_item_id).get()
                if liked_item_doc.exists:
                    st.write(f"- {liked_item_doc.to_dict()['name']}")

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

# 상품 구매 dialog
@st.dialog("shop_demo")
def itemInfo(item):
    # 아이템 이미지 리스트 노출
    cachingImage(item.get("path"))
    # 상품 이름
    st.write(item.get("name"))
    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="center")
    price.write(str(item.get("price","가격 정보 없음"))) # 가격 정보가 없을 수 있으므로 .get 사용 및 문자열 변환
    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{item.get('id')}",
        type="primary",
        use_container_width=True
    )
    if buyBTN:
        # 로그인 정보 없을 경우, 로그인 요청 페이지 스왑
        if not st.session_state.user:
            st.error("구매하려면 로그인이 필요합니다.")
        # 로그인 정보 있을 경우, 구매 페이지 스왑
        else:
            st.session_state.item = item.get("id")
            st.switch_page(page="pages/orderPage.py")

count_in_loop = 0
for line in range(3):
    cols_in_line = st.columns(spec=5, gap="small", vertical_alignment="top")
    for col_idx, i_col in enumerate(cols_in_line):
        with i_col.container(height=400, border=True):
            if items_data and len(items_data) > count_in_loop:
                item = items_data[count_in_loop]
                cachingImage(item.get("path"))
                st.write(f"{item.get("name")}")
                viewBTN = st.button(
                    label="상세보기",
                    key=f"loop_item_{item.get('id')}",
                    type="primary",
                    use_container_width=True
                )
                if viewBTN:
                    itemInfo(item=item)
            else:
                st.write(f"상품 없음 (idx: {count_in_loop})")
            count_in_loop += 1