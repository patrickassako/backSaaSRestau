"""
API routes for Order management module.

Includes public order creation and protected dashboard endpoints.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.core.security import get_current_user
from app.modules.orders import service
from app.modules.orders.schemas import (
    OrderCreate,
    OrderStatusUpdate,
    OrderResponse,
    PublicOrderResponse,
)

router = APIRouter(tags=["Orders"])


# ==================== PUBLIC ENDPOINTS ====================

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate):
    """
    Create a new order from the public website.
    
    This endpoint is PUBLIC and does not require authentication.
    It validates that:
    - The restaurant exists
    - All menu items belong to the restaurant
    - All sides belong to their respective menu items
    
    Returns the created order with calculated total.
    """
    order = service.create_order(data)
    return order


@router.get("/public/orders/{order_code}", response_model=PublicOrderResponse)
async def get_order_by_code(order_code: str):
    """
    Track an order by its short code (first 8 characters of UUID).
    
    This endpoint is PUBLIC.
    """
    order = service.get_order_by_code(order_code)
    return order


# ==================== PROTECTED ENDPOINTS (Dashboard) ====================

@router.get(
    "/restaurants/{restaurant_id}/orders",
    response_model=List[OrderResponse]
)
async def get_restaurant_orders(
    restaurant_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """
    Get all orders for a restaurant.
    
    Requires authentication. Only the restaurant owner can access this.
    Returns orders sorted by created_at DESC with items and sides.
    """
    orders = service.get_restaurant_orders(user_id, restaurant_id)
    return orders


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Update the status of an order.
    
    Requires authentication. Only the restaurant owner can update order status.
    Valid statuses: pending, confirmed, delivered, canceled
    """
    order = service.update_order_status(user_id, order_id, data)
    return order
