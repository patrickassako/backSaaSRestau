from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class RestaurantCreate(BaseModel):
    """Schema for creating a new restaurant."""
    name: str
    slug: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class RestaurantResponse(BaseModel):
    """Schema for restaurant response (authenticated users)."""
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RestaurantPublicResponse(BaseModel):
    """Schema for public restaurant response (no owner_id exposed)."""
    id: UUID
    name: str
    slug: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
