from pydantic import BaseModel
from typing import Optional, List


class RestaurantPublicInfo(BaseModel):
    """Schema for public restaurant information."""
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None

    class Config:
        from_attributes = True


class MenuSidePublic(BaseModel):
    """Public menu side schema."""
    id: str
    name: str
    extra_price: float


class MenuItemPublic(BaseModel):
    """Public menu item schema."""
    id: str
    name: str
    description: Optional[str] = None
    base_price: float
    image_url: Optional[str] = None
    sides: List[MenuSidePublic] = []


class MenuCategoryPublic(BaseModel):
    """Public menu category schema."""
    id: str
    name: str
    items: List[MenuItemPublic] = []


class RestaurantMenuPublic(BaseModel):
    """Public restaurant info for menu response."""
    name: str
    slug: str
    primary_color: Optional[str] = None


class PublicMenuResponse(BaseModel):
    """Full public menu response."""
    restaurant: RestaurantMenuPublic
    categories: List[MenuCategoryPublic] = []

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant": {
                    "name": "Le Petit Bistro",
                    "slug": "le-petit-bistro",
                    "primary_color": "#FF5733"
                },
                "categories": [
                    {
                        "id": "cat-uuid",
                        "name": "Plats",
                        "items": [
                            {
                                "id": "item-uuid",
                                "name": "Poulet braisé",
                                "description": "Poulet grillé aux épices",
                                "base_price": 3500,
                                "image_url": "https://example.com/image.jpg",
                                "sides": [
                                    {"id": "side-uuid", "name": "Plantain", "extra_price": 0},
                                    {"id": "side-uuid-2", "name": "Frites", "extra_price": 500}
                                ]
                            }
                        ]
                    }
                ]
            }
        }
