from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.restaurants.service import user_has_restaurant

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@router.get("/status")
async def get_onboarding_status(user_id: UUID = Depends(get_current_user)):
    """
    Check if the authenticated user has completed onboarding.
    A user is considered onboarded if they own at least one restaurant.
    """
    has_restaurant = user_has_restaurant(user_id)
    
    return {
        "has_restaurant": has_restaurant
    }
