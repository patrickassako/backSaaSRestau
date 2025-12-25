from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class RestaurantCreate(BaseModel):
    """Schema for creating a new restaurant."""
    name: str
    slug: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Le Petit Bistro",
                "slug": "le-petit-bistro",
                "description": "Authentic French cuisine in the heart of the city",
                "cuisine_type": "French",
                "phone": "+1234567890",
                "whatsapp": "+1234567890",
                "email": "contact@lepetitbistro.com",
                "address": "123 Main Street",
                "city": "Paris",
                "country": "France",
                "logo_url": "https://example.supabase.co/storage/v1/object/public/restaurant-assets/logos/logo.jpg",
                "primary_color": "#FF5733"
            }
        }


class RestaurantResponse(BaseModel):
    """Schema for restaurant response (authenticated users)."""
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RestaurantPublicResponse(BaseModel):
    """Schema for public restaurant response (no owner_id exposed)."""
    id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
