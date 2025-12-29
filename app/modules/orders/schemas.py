"""
Pydantic schemas for Order management module.

Handles order creation from public website and order responses for dashboard.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class OrderSideCreate(BaseModel):
    """Schema for selecting a side/accompaniment for an order item."""
    menu_item_side_id: UUID = Field(..., alias="id")
    extra_price: Decimal = Field(..., ge=0, description="Extra price for this side")

    class Config:
        populate_by_name = True
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174002",
                "extra_price": 500
            }
        }


class OrderItemCreate(BaseModel):
    """Schema for a single item in an order."""
    menu_item_id: UUID
    quantity: int = Field(..., gt=0, description="Quantity must be at least 1")
    price: Decimal = Field(..., ge=0, description="Unit price of the item")
    sides: List[OrderSideCreate] = Field(default_factory=list)

    class Config:
        extra = "ignore"
        json_schema_extra = {
            "example": {
                "menu_item_id": "123e4567-e89b-12d3-a456-426614174001",
                "quantity": 2,
                "price": 3500,
                "sides": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174002",
                        "extra_price": 500
                    }
                ]
            }
        }


class OrderCreate(BaseModel):
    """Schema for creating a new order from the public website."""
    restaurant_id: UUID
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: str = Field(..., min_length=8, max_length=20)
    delivery_address: str = Field(..., min_length=5, description="Delivery address is required")
    delivery_note: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "customer_name": "Patrick Essomba",
                "customer_phone": "+237699000000",
                "delivery_address": "Douala, Akwa, Rue de la Joie",
                "delivery_note": "Appeler en arrivant",
                "items": [
                    {
                        "menu_item_id": "123e4567-e89b-12d3-a456-426614174001",
                        "quantity": 2,
                        "price": 3500,
                        "sides": [
                            {
                                "menu_item_side_id": "123e4567-e89b-12d3-a456-426614174002",
                                "extra_price": 500
                            }
                        ]
                    }
                ]
            }
        }


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status."""
    status: str = Field(
        ...,
        pattern="^(pending|confirmed|preparing|ready|delivering|completed|canceled)$",
        description="Order status: pending, confirmed, preparing, ready, delivering, completed, canceled"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "confirmed"
            }
        }


class OrderSideResponse(BaseModel):
    """Schema for order side in response."""
    id: UUID
    order_item_id: UUID
    menu_item_side_id: UUID
    extra_price: float
    side_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    """Schema for order item in response."""
    id: UUID
    order_id: UUID
    menu_item_id: UUID
    quantity: int
    price: float
    item_name: Optional[str] = None
    sides: List[OrderSideResponse] = []

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Schema for full order response."""
    id: UUID
    restaurant_id: UUID
    customer_name: str
    customer_phone: str
    delivery_address: str
    delivery_note: Optional[str] = None
    total_amount: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class PublicOrderResponse(BaseModel):
    """Schema for public order tracking response."""
    order_code: str
    status: str
    total_price: float
    delivery_address: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True
