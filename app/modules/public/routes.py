from fastapi import APIRouter
from app.modules.public import service
from app.modules.public.schemas import RestaurantPublicInfo

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
