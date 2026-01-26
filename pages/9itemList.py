import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='wide',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()
# [모바일 3열 강제 코드 시작]
# 모바일(640px 이하)에서도 컬럼이 수직으로 쌓이지 않고 가로로 유지되도록 강제합니다.
st.html("""
<style>
    @media (max-width: 640px) {
        /* Wrapper Target: Marker가 있는 수직 블록 내부의 모든 HorizontalBlock */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 0 !important;
            padding: 0 !important;
        }

        /* Marker가 있는 수직 블록 내부의 모든 Column */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] {
            flex: 0 0 33.33% !important;
            width: 33.33% !important;
            max-width: 33.33% !important;
            min-width: 0 !important;
            padding: 0 2px !important;
            box-sizing: border-box !important;
            display: block !important;
        }
        
        /* 컬럼 내부 요소 간격 제거 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
            gap: 10 !important;
        }
        
        /* 요소 컨테이너 마진 최소화 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] [data-testid="stElementContainer"] {
            margin: 0 !important;
            min-height: 0 !important;
        }
        
        /* 마크다운 여백 제거 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] [data-testid="stMarkdownContainer"] h6 {
            margin: 0 !important;
            padding: 0 !important;
            line-height: 1.1 !important;
        }

        /* 이미지 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] img {
            width: 100% !important;
            height: auto !important;
            aspect-ratio: 1 / 1 !important;
            object-fit: cover !important;
            max-height: 300px !important;
            border-radius: 4px !important;
            margin: 0 !important;
            display: block !important;
        }

        /* 텍스트 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] h6 {
            font-size: 10px !important;  
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            width: 100% !important;
            padding-top: 2px !important;
        }
        
        /* 숨김 처리 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] p {
             display: none !important; 
        }

        /* 버튼 */
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] button {
            width: 100% !important;
            padding: 0 !important;
            font-size: 9px !important;
            min-height: 20px !important;
            height: 22px !important;
            margin-top: 2px !important;
            line-height: 1 !important; 
            border: 1px solid rgba(0,0,0,0.1) !important;
        }
        
        [data-testid="stVerticalBlock"]:has(.mobile-grid-target) [data-testid="stColumn"] button p {
             display: block !important;
             font-size: 9px !important;
             line-height: 1 !important;
             margin: 0 !important;
             padding: 0 !important;
        }
    }
</style>
""")
# [모바일 3열 강제 코드 끝]
import api
import time
import pandas as pd

utils.init_session()

if st.session_state.page == 'glasses':
    page = {'sort':'glasses'}
elif st.session_state.page == 'sunglasses':
    page = {'sort':'sunglasses'}
elif st.session_state.page == 'sporty':
    page = {'category':'sporty'}
elif st.session_state.page == 'new':
    page = {'event':'new'}
else:
    st.switch_page(page='mainPage.py')

index : str = list(page.keys())[0]

# 아이템 데이터 가져오기
itemData = api.items.showItem()
itemData = itemData[itemData[index] == page.get(index)]

sortedItems = itemData.sort_index()

# Code 정보 가져오기
code_db : dict = utils.utilsDb().firestore_code

# siderbar 정의
with st.sidebar:
    st.page_link(
        page='mainPage.py',
        label='AMUREDO'
    )

    # 회원 로그인 상태 확인
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

grouped_items = sortedItems.groupby('code')

for code, group in grouped_items:
    
    code_info = code_db.get(str(code))
    optimized_code_img = utils.load_and_optimize_from_url(str(code_info['path']))
    if optimized_code_img:
        st.image(optimized_code_img, width='stretch', output_format='WEBP')
    else:
        st.image(str(code_info['path']), width='stretch')

    # 2. 아이템 3열 배치
    # 한번만 Marker를 생성하기 위해 컨테이너로 감쌉니다.
    with st.container():
        st.html('<div class="mobile-grid-target" style="display:none;"></div>')
        for i, (idx, item) in enumerate(group.iterrows()):
            if i % 3 == 0:
                cols = st.columns(3)
            
            col = cols[i % 3]
            with col.container():
                
                # 이미지 표시
                if item['paths']:
                    thumb_img = utils.load_raw_image_from_url(str(item['paths'][0]))
                    if thumb_img:
                        st.image(thumb_img, output_format='WEBP')
                    else:
                        st.image(image=str(item['paths'][0]), output_format='JPEG')
    
                # 정보 표시
                st.markdown(body=f"###### {item['name']}")
                st.markdown(f"###### {item['price']:,}원")
    
                # 상세보기 버튼
                if st.button(
                    label='상세보기',
                    key=f"loop_item_{idx}",
                    type='primary',
                    width='stretch'
                ):
                    st.session_state.item = idx
                    st.switch_page(page="pages/7item.py")

st.divider()
st.html(body=utils.utilsDb().infoAdmin)