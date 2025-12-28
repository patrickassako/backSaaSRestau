from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MenuCategoryCreate(BaseModel):
    """Schema for creating a menu category."""
    restaurant_id: UUID
    name: str
    position: int = 0
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Plats principaux",
                "position": 1,
                "is_active": True
            }
        }


class MenuCategoryUpdate(BaseModel):
    """Schema for updating a menu category."""
    name: Optional[str] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class MenuCategoryResponse(BaseModel):
    """Schema for menu category response."""
    id: UUID
    restaurant_id: UUID
    name: str
    position: int
    is_active: bool

    class Config:
        from_attributes = True
