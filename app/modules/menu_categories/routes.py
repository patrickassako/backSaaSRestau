from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_user
from app.modules.menu_categories import service
from app.modules.menu_categories.schemas import (
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuCategoryResponse,
)

router = APIRouter(prefix="/menu/categories", tags=["Menu Categories"])


@router.post("", response_model=MenuCategoryResponse)
async def create_category(
    data: MenuCategoryCreate,
    user_id: UUID = Depends(get_current_user),
):
    """Create a new menu category. Requires authentication."""
    category = service.create_category(user_id, data)
    return category


@router.get("", response_model=List[MenuCategoryResponse])
async def get_categories(
    restaurant_id: UUID = Query(..., description="Restaurant ID"),
    user_id: UUID = Depends(get_current_user),
):
    """Get all menu categories for a restaurant. Requires authentication."""
    categories = service.get_categories(user_id, restaurant_id)
    return categories


@router.patch("/{category_id}", response_model=MenuCategoryResponse)
async def update_category(
    category_id: UUID,
    data: MenuCategoryUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """Update a menu category. Requires authentication."""
    category = service.update_category(user_id, category_id, data)
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """Delete a menu category. Requires authentication."""
    service.delete_category(user_id, category_id)
    return None
