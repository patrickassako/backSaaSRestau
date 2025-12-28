from typing import Optional
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client


def get_public_restaurant_by_slug(slug: str) -> Optional[dict]:
    """
    Returns public restaurant information by slug.
    Only returns fields safe for public exposure.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("name, slug, description, logo_url, primary_color, address, city, country, phone, whatsapp")
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
