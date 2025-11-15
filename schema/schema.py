from pydantic import BaseModel, EmailStr, Field, HttpUrl

class user(BaseModel):
    email : EmailStr = Field(title='userEmail')
    name: str = Field(title='userName')
    phoneNumber: str = Field(title='userPhoneNumber')
    age : int = Field(title='userAge')
    address : dict | None = Field(title='userAddress')

class item(BaseModel):
    category : str = Field(title='itemCategory')
    color : str = Field(title='itemColor')
    series : str = Field(title='itemSerises')
    paths : list[HttpUrl] = Field(title='itemImagePaths')
    name : str = Field(title='itemName')
    detail : HttpUrl = Field(title='itemDetail')
    price : int = Field(title='itemPrice')
    discount : int = Field(title='itemDiscount')
    event : str | None = Field(default=None, title='itemEvent')

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