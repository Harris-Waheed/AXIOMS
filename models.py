from pydantic import BaseModel, Field


class OrderIn(BaseModel):

    customer_name: str = Field(..., max_length=40)
    customer_number: str = Field(..., max_length=13)
    customer_city : str = Field(..., max_length=100)
    customer_address: str = Field(..., max_length=200)
    customer_bill : int = Field(..., gt=0)


class OrderOut(BaseModel):

    customer_name: str
    customer_address: str
    customer_bill: int

