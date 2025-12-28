from fastapi import APIRouter
from app.modules.public import service
from app.modules.public.schemas import RestaurantPublicInfo, PublicMenuResponse

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/restaurants/{slug}", response_model=RestaurantPublicInfo)
async def get_public_restaurant(slug: str):
    """
    Get public restaurant information by slug.
    No authentication required.
    Returns only public fields (no id, owner_id, timestamps, etc.)
    """
    restaurant = service.get_public_restaurant_by_slug(slug)
    return restaurant


@router.get("/restaurants/{slug}/menu", response_model=PublicMenuResponse)
async def get_public_menu(slug: str):
    """
    Get public menu for a restaurant by slug.
    No authentication required.
    Returns categories with items and sides.
    """
    menu = service.get_public_menu_by_slug(slug)
    return menu
