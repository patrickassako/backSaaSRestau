from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.restaurants.schemas import RestaurantCreate


def create_restaurant(user_id: UUID, data: RestaurantCreate) -> dict:
    """
    Creates a new restaurant owned by the specified user.
    """
    supabase = get_supabase_client()

    restaurant_data = {
        "name": data.name,
        "slug": data.slug,
        "owner_id": str(user_id),
        "phone": data.phone,
        "email": data.email,
        "address": data.address,
        "city": data.city,
        "country": data.country,
        "is_active": True,
    }

    try:
        response = supabase.table("restaurants").insert(restaurant_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create restaurant",
            )

        return response.data[0]

    except Exception as e:
        # Handle unique constraint violation for slug
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A restaurant with this slug already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_my_restaurants(user_id: UUID) -> List[dict]:
    """
    Returns all restaurants owned by the specified user.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("*")
            .eq("owner_id", str(user_id))
            .execute()
        )

        return response.data or []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_restaurant_by_slug(slug: str) -> Optional[dict]:
    """
    Returns a restaurant by its slug.
    Used for public access - owner_id should be stripped by the route.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("*")
            .eq("slug", slug)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        if "no rows" in str(e).lower() or "0 rows" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def user_has_restaurant(user_id: UUID) -> bool:
    """
    Checks if a user owns at least one restaurant.
    Used for onboarding flow verification.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("id", count="exact")
            .eq("owner_id", str(user_id))
            .limit(1)
            .execute()
        )

        return response.count is not None and response.count > 0

    except Exception:
        # In case of error, return False to be safe
        return False
