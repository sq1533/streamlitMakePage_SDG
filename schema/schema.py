from pydantic import BaseModel, EmailStr, Field, HttpUrl, field_validator, field_serializer
from typing import Optional, Dict, Any

class user(BaseModel):
    email : EmailStr = Field(title='userEmail')
    name: str = Field(title='userName')
    phoneNumber: str = Field(title='userPhoneNumber')
    age : int = Field(title='userAge')
    address: Optional[Dict[str, Any]] = Field(default=None, title='userAddress')
    orderList: Optional[Dict[str, Any]] = Field(default=None)
    @field_validator('address', 'orderList', mode='before') 
    @classmethod
    def empty_string_to_none(cls, v):
        if v == '':
            return None
        return v

    @field_serializer('address', 'orderList')
    def none_to_empty_string(self, v, _info):
        if v is None:
            return ''
        return v

class item(BaseModel):
    created_at : int = Field(default=0, title='itemCreatedAt')
    name : str = Field(title='itemName')
    category : str = Field(title='itemCategory')
    color : str = Field(title='itemColor')
    series : str = Field(title='itemSerises')
    sort : str = Field(title='glasses / sunglasses')

    paths : list[HttpUrl] = Field(title='itemImagePaths')
    detail : HttpUrl = Field(title='itemDetail')
    package : HttpUrl = Field(title='itemPackage')

    price : int = Field(title='itemPrice')
    event : Optional[str] = Field(default=None, title='itemEvent')

    sales : Optional[int] = 0
    point : Optional[int] = 0

class itemFeedback(BaseModel):
    count : int = Field(title='feedbackCount')
    point : int = Field(title='feedbackPoint')
    text : dict = Field(title='feedbackText')

class itemStatus(BaseModel):
    enable : bool = Field(title='itemEnable')
    count : int = Field(title='itemAmount')
    sales : int = Field(title='itemSales')
    refund : int = Field(title='itemRefunds')
    feedback : itemFeedback = Field(title='itemFeedback')