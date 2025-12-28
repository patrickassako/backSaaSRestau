from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.menu_categories.schemas import MenuCategoryCreate, MenuCategoryUpdate


def verify_restaurant_ownership(user_id: UUID, restaurant_id: UUID) -> bool:
    """Verify that the user owns the restaurant."""
    supabase = get_supabase_client()
    
    try:
        response = (
            supabase.table("restaurants")
            .select("id")
            .eq("id", str(restaurant_id))
            .eq("owner_id", str(user_id))
            .single()
            .execute()
        )
        return response.data is not None
    except Exception:
        return False


def create_category(user_id: UUID, data: MenuCategoryCreate) -> dict:
    """Create a new menu category."""
    if not verify_restaurant_ownership(user_id, data.restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant",
        )

    supabase = get_supabase_client()

    category_data = {
        "restaurant_id": str(data.restaurant_id),
        "name": data.name,
        "position": data.position,
        "is_active": data.is_active,
    }

    try:
        response = supabase.table("menu_categories").insert(category_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create category",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_categories(user_id: UUID, restaurant_id: UUID) -> List[dict]:
    """Get all menu categories for a restaurant."""
    if not verify_restaurant_ownership(user_id, restaurant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this restaurant",
        )

    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("menu_categories")
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


def update_category(user_id: UUID, category_id: UUID, data: MenuCategoryUpdate) -> dict:
    """Update a menu category."""
    supabase = get_supabase_client()

    # Get category and verify ownership
    try:
        category = (
            supabase.table("menu_categories")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(category_id))
            .single()
            .execute()
        )

        if not category.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if category.data["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this category",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Update
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        response = (
            supabase.table("menu_categories")
            .update(update_data)
            .eq("id", str(category_id))
            .execute()
        )

        return response.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def delete_category(user_id: UUID, category_id: UUID) -> None:
    """Delete a menu category."""
    supabase = get_supabase_client()

    # Get category and verify ownership
    try:
        category = (
            supabase.table("menu_categories")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(category_id))
            .single()
            .execute()
        )

        if not category.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if category.data["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this category",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    try:
        supabase.table("menu_categories").delete().eq("id", str(category_id)).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
