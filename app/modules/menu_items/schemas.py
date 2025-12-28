from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MenuItemCreate(BaseModel):
    """Schema for creating a menu item."""
    restaurant_id: UUID
    category_id: UUID
    name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_available: bool = True
    position: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant_id": "123e4567-e89b-12d3-a456-426614174000",
                "category_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Poulet braisé",
                "description": "Poulet grillé aux épices africaines",
                "base_price": 3500,
                "image_url": "https://example.com/image.jpg",
                "is_available": True,
                "position": 1
            }
        }


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    position: Optional[int] = None


class MenuItemResponse(BaseModel):
    """Schema for menu item response."""
    id: UUID
    restaurant_id: UUID
    category_id: UUID
    name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    is_available: bool
    position: int

    class Config:
        from_attributes = True
