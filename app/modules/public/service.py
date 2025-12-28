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


def get_public_menu_by_slug(slug: str) -> dict:
    """
    Returns the full public menu for a restaurant.
    Includes categories, items, and sides.
    """
    supabase = get_supabase_client()

    # Get restaurant info
    try:
        restaurant = (
            supabase.table("restaurants")
            .select("id, name, slug, primary_color")
            .eq("slug", slug)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not restaurant.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

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

    restaurant_id = restaurant.data["id"]

    # Get categories
    try:
        categories_response = (
            supabase.table("menu_categories")
            .select("id, name, position")
            .eq("restaurant_id", restaurant_id)
            .eq("is_active", True)
            .order("position")
            .execute()
        )

        categories = categories_response.data or []

    except Exception:
        categories = []

    # Get items with sides
    try:
        items_response = (
            supabase.table("menu_items")
            .select("id, category_id, name, description, base_price, image_url, menu_item_sides(id, name, extra_price, is_required, position)")
            .eq("restaurant_id", restaurant_id)
            .eq("is_available", True)
            .order("position")
            .execute()
        )

        items = items_response.data or []

    except Exception:
        items = []

    # Build response structure
    categories_with_items = []
    for category in categories:
        category_items = []
        for item in items:
            if item["category_id"] == category["id"]:
                # Sort sides by position
                sides = sorted(
                    item.get("menu_item_sides", []),
                    key=lambda x: x.get("position", 0)
                )
                category_items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "description": item.get("description"),
                    "base_price": item["base_price"],
                    "image_url": item.get("image_url"),
                    "sides": [
                        {
                            "id": side["id"],
                            "name": side["name"],
                            "extra_price": side["extra_price"],
                        }
                        for side in sides
                    ]
                })

        categories_with_items.append({
            "id": category["id"],
            "name": category["name"],
            "items": category_items
        })

    return {
        "restaurant": {
            "name": restaurant.data["name"],
            "slug": restaurant.data["slug"],
            "primary_color": restaurant.data.get("primary_color"),
        },
        "categories": categories_with_items
    }
