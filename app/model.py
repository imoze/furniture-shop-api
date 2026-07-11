from datetime import date as date_type
from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    '''Basic error model'''

    detail: str = Field(
        description='Human readable error description',
        examples=['Furniture not found'],
    )


class FurnitureOut(BaseModel):
    '''Furniture item'''

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Internal furniture ID', examples=[1])
    name: str = Field(description='Furniture name', examples=['Chair'])
    price: float = Field(description='Price per piece, $', examples=[149.99])
    category: str = Field(description='Furniture category', examples=['chairs'])


class OrderItemOut(BaseModel):
    '''Item within order'''

    model_config = ConfigDict(from_attributes=True)

    furniture_id: int = Field(description="Ordered furniture ID", examples=[1])
    name: str = Field(description="Furniture name", examples=["Chair"])
    price: float = Field(description="Price per piece, $", examples=[149.99])
    quantity: int = Field(description="Ordered quantity", examples=[2])


class OrderOut(BaseModel):
    '''Order summary, without items'''

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='Order ID', examples=[17])
    email: str = Field(description='Customer email', examples=['ivan@example.com'])
    total_price: float = Field(description='Total order sum, $', examples=[449.97])
    date: date_type = Field(description='Order date', examples=['2026-07-11'])


class OrderDetailOut(OrderOut):
    '''Order with its items'''

    items: list[OrderItemOut] = Field(
        default_factory=list,
        description='Order items',
    )