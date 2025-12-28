from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.modules.menu_items import service
from app.modules.menu_items.schemas import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemResponse,
)

router = APIRouter(prefix="/menu/items", tags=["Menu Items"])


@router.post("", response_model=MenuItemResponse)
async def create_item(
    data: MenuItemCreate,
    user_id: UUID = Depends(get_current_user),
):
    """Create a new menu item. Requires authentication."""
    item = service.create_item(user_id, data)
    return item


@router.get("", response_model=List[MenuItemResponse])
async def get_items(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    user_id: UUID = Depends(get_current_user),
):
    """Get all menu items for a restaurant. Requires authentication."""
    items = service.get_items(user_id, restaurant_id)
    return items


@router.patch("/{item_id}", response_model=MenuItemResponse)
async def update_item(
    item_id: UUID,
    data: MenuItemUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """Update a menu item. Requires authentication."""
    item = service.update_item(user_id, item_id, data)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(
    item_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """Delete a menu item. Requires authentication."""
    service.delete_item(user_id, item_id)
    return None
