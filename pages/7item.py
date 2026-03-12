import streamlit as st
import utils

# 페이지 기본 설정
st.set_page_config(
    page_title='AMUREDO',
    page_icon=utils.utilsDb().pageIcon,
    layout='centered',
    initial_sidebar_state='auto'
)
# 페이지 UI 변경 사항
utils.set_page_ui()

from pandas import DataFrame
import api

# 페이지 세션 관리
if 'item' not in st.session_state:
    st.session_state.item = {
        'item' : '',
        'itemKey' : 0
    }
if 'selectedColor' not in st.session_state:
    st.session_state.selectedColor = None

# 파라미터 접근 확인
if "item_id" in st.query_params:
    st.session_state.item['item'] = st.query_params["item_id"]

# 페이지 접근 검증
if st.session_state.item['item'] == '':
    st.switch_page(page='mainPage.py')

# 데이터 불러오기
allItem : DataFrame = api.items.showItem()
itemCode : str = st.session_state.item['item']

filtered_item = allItem[allItem['code'] == itemCode]

colorOption = filtered_item['color'].tolist()

itemInfo = filtered_item.iloc[st.session_state.item['itemKey']]

with open("database/docs.html", "r", encoding="utf-8") as f:
    catalog = f.read()


# 컬러 옵션 변경
def choose_color():
    selected_color = st.session_state.selectedColor

    color_list = filtered_item['color'].tolist()
    itemIndex = color_list.index(selected_color)

    st.session_state.item['itemKey'] = itemIndex

# 페이지 시작
with st.container(horizontal=True):
    st.markdown(body=f"#### :gray[amuredo > {itemInfo['sort']}]")
    st.space(size='stretch')
    with st.popover(label='공유하기'):
        st.code(f"https://amuredo.shop/item?item_id={itemCode}", language="text")

name, another = st.columns(spec=[4,1], gap='small', vertical_alignment='bottom')

name.markdown(f"# {itemInfo['name']}")
another.selectbox(
    label='컬러',
    options=colorOption,
    key='selectedColor',
    on_change=choose_color,
    placeholder='다른 옵션',
    label_visibility='collapsed',
    width='stretch'
)

with st.container(horizontal=True):
    st.markdown(body=f"### {itemInfo['price']:,}원")
    st.space(size='stretch')    
    st.link_button(
        label='네이버 스토어 구매',
        url=f"{itemInfo['naver']}",
        type='secondary',
        width='stretch'
    )

design, info = st.tabs(tabs=['design', 'information'])

with design:
    st.html(catalog)
    st.image(str(itemInfo['paths'][1]))

with info:
    st.image(str(itemInfo['detail']))

with st.sidebar:
    utils.set_sidebarLogo()
    utils.set_sidebar()