"""
Schémas Pydantic pour les restaurants.
Utilisés pour la validation des entrées et les réponses API.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class RestaurantCreate(BaseModel):
    """Schéma pour créer un nouveau restaurant."""
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
    """Schéma de réponse pour les utilisateurs authentifiés (avec owner_id)."""
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
    """
    Schéma de réponse publique (sans owner_id, is_active, created_at).
    Utilisé pour l'endpoint GET /restaurants/{slug} accessible au rôle public.
    """
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

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
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
