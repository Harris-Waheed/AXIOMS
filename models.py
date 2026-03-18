from pydantic import BaseModel, Field


class OrderIn(BaseModel):

    customer_name: str = Field(..., max_length=40)
    customer_number: str = Field(..., max_length=13)
    customer_city : str = Field(..., max_length=100)
    customer_address: str = Field(..., max_length=200)
    customer_bill : int = Field(..., gt=0)
    product_id : int = Field(...)


class OrderOut(BaseModel):

    customer_name: str
    customer_number: str
    customer_city : str
    customer_address: str
    customer_bill: int
    order_date : str
    product_id : int
    order_id: int


class InventoryIn(BaseModel):

    product_name : str = Field(..., max_length=100)
    product_description : str = Field(..., max_length=1000)
    product_wholesale : int
    product_retail : int
    product_image : str


class InventoryOut(BaseModel):

    product_id : int
    product_name : str
    product_description: str
    product_wholesale: int
    product_retail: int
    product_image: str
