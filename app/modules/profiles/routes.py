from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.profiles import service
from app.modules.profiles.schemas import ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(user_id: UUID = Depends(get_current_user)):
    """
    Get the current user's profile.
    Requires authentication.
    """
    profile = service.get_profile(user_id)
    return profile


@router.patch("/me", response_model=ProfileResponse)
async def update_my_profile(
    data: ProfileUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Update the current user's profile.
    Requires authentication.
    Only updates fields that are provided.
    """
    profile = service.update_profile(user_id, data)
    return profile
