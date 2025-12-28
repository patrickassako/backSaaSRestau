from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.menu_items.schemas import MenuItemCreate, MenuItemUpdate
from app.modules.menu_categories.service import verify_restaurant_ownership


def create_item(user_id: UUID, data: MenuItemCreate) -> dict:
    """Create a new menu item."""
    if not verify_restaurant_ownership(user_id, data.restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant",
        )

    supabase = get_supabase_client()

    item_data = {
        "restaurant_id": str(data.restaurant_id),
        "category_id": str(data.category_id),
        "name": data.name,
        "description": data.description,
        "base_price": data.base_price,
        "image_url": data.image_url,
        "is_available": data.is_available,
        "position": data.position,
    }

    try:
        response = supabase.table("menu_items").insert(item_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create menu item",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_items(user_id: UUID, restaurant_id: UUID) -> List[dict]:
    """Get all menu items for a restaurant."""
    if not verify_restaurant_ownership(user_id, restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant",
        )

    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("menu_items")
            .select("*")
            .eq("restaurant_id", str(restaurant_id))
            .order("position")
            .execute()
        )

        return response.data or []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def update_item(user_id: UUID, item_id: UUID, data: MenuItemUpdate) -> dict:
    """Update a menu item."""
    supabase = get_supabase_client()

    # Get item and verify ownership
    try:
        item = (
            supabase.table("menu_items")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(item_id))
            .single()
            .execute()
        )

        if not item.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )

        if item.data["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this item",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    # Update
    update_data = {}
    for k, v in data.model_dump().items():
        if v is not None:
            if k == "category_id":
                update_data[k] = str(v)
            else:
                update_data[k] = v

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        response = (
            supabase.table("menu_items")
            .update(update_data)
            .eq("id", str(item_id))
            .execute()
        )

        return response.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def delete_item(user_id: UUID, item_id: UUID) -> None:
    """Delete a menu item."""
    supabase = get_supabase_client()

    # Get item and verify ownership
    try:
        item = (
            supabase.table("menu_items")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(item_id))
            .single()
            .execute()
        )

        if not item.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )

        if item.data["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this item",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    try:
        supabase.table("menu_items").delete().eq("id", str(item_id)).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
