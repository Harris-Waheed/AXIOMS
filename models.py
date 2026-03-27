from pydantic import BaseModel, Field, HttpUrl
from typing import List

class CartItems(BaseModel):

    product_id : int
    quantity : int

class OrderIn(BaseModel):

    customer_name: str = Field(..., max_length=40)
    customer_number: str = Field(..., max_length=13)
    customer_city : str = Field(..., max_length=100)
    customer_address: str = Field(..., max_length=200)
    customer_bill : int = Field(..., gt=0)
    cart_items : List[CartItems]

class OrderCustomerOut(BaseModel):

    customer_name: str
    customer_number: str
    customer_city : str
    customer_address: str
    customer_bill: int
    order_date : str
    order_id: int


class InventoryIn(BaseModel):

    product_name : str = Field(..., max_length=100)
    product_description : str = Field(..., max_length=1000)
    product_wholesale : int
    product_retail : int
    product_image : str
    product_category : str
    product_link : HttpUrl | None = None  # "HttpUrl OR None". Default is None.

class InventoryCustomerOut(BaseModel):

    product_id : int
    product_name : str
    product_description: str
    product_retail: int
    product_image: str
    product_category : str
