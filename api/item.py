import streamlit as st
import pandas as pd
import utils

class items(utils.database):

    # 아이템 ID 정보 조회
    @st.cache_data(ttl=36000)
    def showItem() -> pd.DataFrame:
        if utils.utilsDb().fs_client:
            utils.utilsDb().refresh_items()
            
        itemInfo : dict = utils.utilsDb().firestore_item
        keys = list(itemInfo.keys())
        items = []
        for key in keys:
            items.append(itemInfo.get(key))

        itemData = pd.DataFrame(
            data=items,
            index=keys,
            columns=[
                'created_at',
                'series',
                'sort',
                'code',
                'category',
                'name',
                'naver',
                'color',
                'event',
                'price',
                'paths',
                'detail'
                ]
            )
        return itemData

    # 특정 아이템 수량 및 상태
    def itemStatus(itemId : str) -> dict:
        try:
            itemStatus : dict = utils.utilsDb().realtimeDB.reference(path=f"itemStatus/{itemId}").get()
            return itemStatus
        except Exception as e:
            return {'failed' : str(e)}