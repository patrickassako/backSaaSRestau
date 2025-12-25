from pydantic import BaseModel
from typing import Optional


class ProfileUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "phone": "+1234567890",
                "avatar_url": "https://example.supabase.co/storage/v1/object/public/restaurant-assets/avatars/user123.jpg"
            }
        }


class ProfileResponse(BaseModel):
    """Schema for profile response."""
    id: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    is_onboarded: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "full_name": "John Doe",
                "phone": "+1234567890",
                "avatar_url": "https://example.supabase.co/storage/v1/object/public/restaurant-assets/avatars/user123.jpg",
                "is_onboarded": True
            }
        }
