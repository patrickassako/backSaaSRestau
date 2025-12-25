from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.profiles.schemas import ProfileUpdate


def get_profile(user_id: UUID) -> Optional[dict]:
    """
    Retrieves the profile for the specified user.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("profiles")
            .select("*")
            .eq("id", str(user_id))
            .single()
            .execute()
        )

        return response.data

    except Exception as e:
        if "no rows" in str(e).lower() or "0 rows" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def update_profile(user_id: UUID, data: ProfileUpdate) -> dict:
    """
    Updates the profile for the specified user.
    Only updates fields that are provided (non-None).
    """
    supabase = get_supabase_client()

    # Build update data with only non-None fields
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        response = (
            supabase.table("profiles")
            .update(update_data)
            .eq("id", str(user_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )
