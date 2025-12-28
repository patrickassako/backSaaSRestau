from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.menu_sides.schemas import MenuSideCreate, MenuSideUpdate


def verify_item_ownership(user_id: UUID, item_id: UUID) -> bool:
    """Verify that the user owns the menu item's restaurant."""
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("menu_items")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(item_id))
            .single()
            .execute()
        )

        if not response.data:
            return False

        return response.data["restaurants"]["owner_id"] == str(user_id)

    except Exception:
        return False


def create_side(user_id: UUID, data: MenuSideCreate) -> dict:
    """Create a new menu item side/accompaniment."""
    if not verify_item_ownership(user_id, data.menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this menu item",
        )

    supabase = get_supabase_client()

    side_data = {
        "menu_item_id": str(data.menu_item_id),
        "name": data.name,
        "extra_price": data.extra_price,
        "is_required": data.is_required,
        "position": data.position,
    }

    try:
        response = supabase.table("menu_item_sides").insert(side_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create side",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def update_side(user_id: UUID, side_id: UUID, data: MenuSideUpdate) -> dict:
    """Update a menu item side."""
    supabase = get_supabase_client()

    # Get side and verify ownership
    try:
        side = (
            supabase.table("menu_item_sides")
            .select("*, menu_items!inner(*, restaurants!inner(owner_id))")
            .eq("id", str(side_id))
            .single()
            .execute()
        )

        if not side.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Side not found",
            )

        if side.data["menu_items"]["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this side",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Side not found",
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
            supabase.table("menu_item_sides")
            .update(update_data)
            .eq("id", str(side_id))
            .execute()
        )

        return response.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def delete_side(user_id: UUID, side_id: UUID) -> None:
    """Delete a menu item side."""
    supabase = get_supabase_client()

    # Get side and verify ownership
    try:
        side = (
            supabase.table("menu_item_sides")
            .select("*, menu_items!inner(*, restaurants!inner(owner_id))")
            .eq("id", str(side_id))
            .single()
            .execute()
        )

        if not side.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Side not found",
            )

        if side.data["menu_items"]["restaurants"]["owner_id"] != str(user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to this side",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Side not found",
        )

    try:
        supabase.table("menu_item_sides").delete().eq("id", str(side_id)).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
