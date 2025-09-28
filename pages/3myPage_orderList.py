import streamlit as st
import utils
import itemFunc.itemInfo as itemInfo
from datetime import datetime

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
# 주문 상품 정보
if 'orderItem' not in st.session_state:
    st.session_state.orderItem = None

st.html(
    body="""
    <style>
    div[data-testid="stElementToolbar"] {
        display: none !important;
    }
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    </style>
    """
)

# 상품 상세페이지 dialog
@st.dialog(title='상품 상세', width='large')
def showItem(itemId, itemIF):
    buyDisable = not itemInfo.items.itemStatus(itemId=itemId)['enable']
    st.html(body=f'<img src={itemIF['paths'][0]} alt="image sunglasses01" style="width: 100%; height: auto; display: block;"/>')
    st.html(body=f'<img src={itemIF['paths'][1]} alt="image sunglasses02" style="width: 100%; height: auto; display: block;"/>')
    st.html(body=f'<img src={itemIF['paths'][2]} alt="image sunglasses03" style="width: 100%; height: auto; display: block;"/>')

    # 상품 이름
    st.markdown(f"# {itemIF['name']}")

    # 상품 가격 및 구매 버튼
    price, buy = st.columns(spec=2, gap="small", vertical_alignment="top")
    price.markdown(f"#### 상품 가격 : ~~{int((itemIF['price']*100/(100-itemIF['discount'])//100)*100)}~~ {itemIF['price']}원( :red[-{itemIF['discount']}%] )")

    buyBTN = buy.button(
        label="구매하기",
        key=f"buyItem_{itemId}",
        type="primary",
        disabled=buyDisable,
        use_container_width=True
    )
    with st.expander(label="상품 세부정보"):
        st.html(body=f"{itemIF['detail']}")

    if buyBTN:
        st.session_state.item = itemId
        st.switch_page(page="pages/5orderPage.py")

if any(value is not None for value in st.session_state.token.values()):
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

        if 'orderList' in st.session_state.user:
            for key, order in reversed(st.session_state.user.get('orderList').items()):
                # 주문 정보
                orderTime = key
                itemID = order.get('item')
                address = order.get('address')
                status = utils.database().showStatus[order.get('status')]

                # 아이템 정보
                itemIF = itemInfo.items.itemInfo()[itemID]

                with st.expander(label=f'주문 날짜 : {datetime.strptime(orderTime, '%y%m%d%H%M%S')} // {itemIF.get('name')} {status}'):
                    image, info = st.columns(spec=[1,2], gap="small", vertical_alignment="top")
                    image.image(
                        image=itemIF.get("paths")[0],
                        caption=None,
                        use_container_width=True,
                        clamp=False,
                        output_format="auto"
                        )
                    info.markdown(
                        body=f"""
                        상품명 : {itemIF.get('name')}\n\n
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
                            'switchPagePath':'pages/4myOrder_itemCancel.py', # 페이지 이동
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
                            'switchPagePath':'pages/4myOrder_itemRefund.py', # 페이지 이동
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
                        st.switch_page(page='pages/4myOrder_changeAddr.py')

                    aboutItemB = aboutItem.button(
                        label='상품 상세',
                        key=f'item_{key}',
                        type='primary',
                        use_container_width=True
                    )
                    if aboutItemB:
                        showItem(itemId=itemID, itemIF=itemIF)

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