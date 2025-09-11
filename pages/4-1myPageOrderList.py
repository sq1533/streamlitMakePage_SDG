import streamlit as st
import utils
from datetime import datetime

# 회원 로그인 구분
if 'user' not in st.session_state:
    st.session_state.user = None
# 회원 정보
if 'userInfo' not in st.session_state:
    st.session_state.userInfo = None

# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = False

st.markdown(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    div[aria-label="dialog"][role="dialog"] {
        width: 75% !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
    itemInfo = utils.items.itemInfo(itemId=item)['result']
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
        st.html(body=f"{itemInfo['detail']}")
    if buyBTN:
        st.session_state.item = item
        st.switch_page(page="pages/5-1orderPage.py")

if st.session_state.user:
    with st.sidebar:
        st.title(body="주문내역")

    empty, main, empty = st.columns(spec=[1,4,1], gap="small", vertical_alignment="top")

    with main.container():
        # 홈으로 이동
        goHome = st.button(
            label='HOME',
            key='goHOME',
            type='primary',
            use_container_width=False,
            disabled=False
        )
        if goHome:
            st.switch_page(page="mainPage.py")
        
        st.markdown(body="주문 내역")

        if st.session_state.userInfo and ('orderList' in st.session_state.userInfo):
            for key, order in reversed(st.session_state.userInfo.get('orderList').items()):
                # 주문 정보
                orderTime = key
                itemID = order.get('item')
                address = order.get('address')
                status = utils.database().showStatus[order.get('status')]

                # 아이템 정보
                itemInfo = utils.items.itemInfo(itemId=itemID)['result']

                with st.expander(label=f'주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemInfo.get('name')} {status}'):
                    image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                    image.image(
                        image=itemInfo.get("paths")[0],
                        caption=None,
                        use_container_width=True,
                        clamp=False,
                        output_format="auto"
                        )
                    info.markdown(
                        body=f"""
                        상품명 : {itemInfo.get('name')}\n\n
                        {address}
                        """
                        )
                    
                    changeAddr, aboutItem, changeStatus = st.columns(spec=3, gap="small", vertical_alignment="center")

                    # 상품 준비중
                    if order.get('status') == 'ready':
                        btnStatus = {
                            'addressChange':False, # 배송지 변경 버튼 활성화 여부
                            'cancelB':False, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'주문 취소', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'pages/4-3userCancel.py', # 페이지 이동
                        }
                    # 배송 완료 후 7일 경과
                    elif order.get('status') == 'Done':
                        btnStatus = {
                            'addressChange':True, # 배송지 변경 버튼 활성화 여부
                            'cancelB':True, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'완료', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'mainPage.py', # 페이지 이동
                        }
                    # 상품 취소
                    elif order.get('status') == 'cancel':
                        btnStatus = {
                            'addressChange':True, # 배송지 변경 버튼 활성화 여부
                            'cancelB':True, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'취소 완료', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'mainPage.py', # 페이지 이동
                        }
                    # 상품 환불 요청
                    elif order.get('status') == 'refund':
                        btnStatus = {
                            'addressChange':True, # 배송지 변경 버튼 활성화 여부
                            'cancelB':True, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'환불 진행 중..', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'mainPage.py', # 페이지 이동
                        }
                    # 상품 환불 완료
                    elif order.get('status') == 'refunded':
                        btnStatus = {
                            'addressChange':True, # 배송지 변경 버튼 활성화 여부
                            'cancelB':True, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'환불 완료', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'mainPage.py', # 페이지 이동
                        }
                    #상품 배송중, 상품 배송완료( 7일 경과 전 )
                    else:
                        btnStatus = {
                            'addressChange':True, # 배송지 변경 버튼 활성화 여부
                            'cancelB':False, # 주문 상태 변경 버튼 활성화 여부
                            'statusChange':'환불 요청', # 주문 상태 변경 버튼 멘트
                            'switchPagePath':'pages/4-4userRefund.py', # 페이지 이동
                        }

                    changeAddrB = changeAddr.button(
                        label='배송지 변경',
                        key=f'address_{key}',
                        type='primary',
                        disabled=btnStatus['addressChange'],
                        use_container_width=True
                    )
                    if changeAddrB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page='pages/4-2userCgAddr.py')

                    aboutItemB = aboutItem.button(
                        label='상품 상세',
                        key=f'item_{key}',
                        type='primary',
                        use_container_width=True
                    )
                    if aboutItemB:
                        showItem(item=itemID)

                    chagneStatusB = changeStatus.button(
                        label=btnStatus['statusChange'],
                        key=f'order_{key}',
                        type='primary',
                        disabled=btnStatus['cancelB'],
                        use_container_width=True
                    )
                    if chagneStatusB:
                        st.session_state.orderItem = [key, order]
                        st.switch_page(page=btnStatus['switchPagePath'])
        else:
            st.info(body="주문내역 확인 불가")
else:
    st.switch_page(page="mainPage.py")