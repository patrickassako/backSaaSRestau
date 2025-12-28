from pydantic import BaseModel
from typing import Optional


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
        json_schema_extra = {
            "example": {
                "name": "Le Petit Bistro",
                "slug": "le-petit-bistro",
                "description": "Authentic French cuisine",
                "logo_url": "https://example.supabase.co/storage/v1/object/public/restaurant-assets/logos/logo.jpg",
                "primary_color": "#FF5733",
                "address": "123 Main Street",
                "city": "Paris",
                "country": "France",
                "phone": "+1234567890",
                "whatsapp": "+1234567890"
            }
        }
