from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.restaurants import service
from app.modules.restaurants.schemas import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantPublicResponse,
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("", response_model=RestaurantResponse)
async def create_restaurant(
    data: RestaurantCreate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Create a new restaurant.
    Requires authentication. The restaurant will be owned by the current user.
    """
    restaurant = service.create_restaurant(user_id=user_id, data=data)
    return restaurant


@router.get("/me", response_model=List[RestaurantResponse])
async def get_my_restaurants(
    user_id: UUID = Depends(get_current_user),
):
    """
    Get all restaurants owned by the current user.
    Requires authentication.
    """
    restaurants = service.get_my_restaurants(user_id=user_id)
    return restaurants


@router.get("/{slug}", response_model=RestaurantPublicResponse)
async def get_restaurant_by_slug(slug: str):
    """
    Get a restaurant by its slug.
    Public endpoint - does not expose owner_id.
    """
    restaurant = service.get_restaurant_by_slug(slug=slug)
    return restaurant
