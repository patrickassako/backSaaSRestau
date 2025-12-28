"""
Schémas Pydantic pour les endpoints publics.
"""
from pydantic import BaseModel
from typing import Optional, List


class RestaurantPublicInfo(BaseModel):
    """Informations publiques d'un restaurant."""
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
    """Accompagnement public."""
    id: str
    name: str
    extra_price: float


class MenuItemPublic(BaseModel):
    """Plat public avec ses accompagnements."""
    id: str
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    sides: List[MenuSidePublic] = []


class MenuCategoryPublic(BaseModel):
    """Catégorie de menu avec ses plats."""
    category_id: str
    name: str
    items: List[MenuItemPublic] = []


class RestaurantMenuInfo(BaseModel):
    """Informations restaurant pour le menu."""
    name: str
    slug: str
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None


class PublicMenuResponse(BaseModel):
    """
    Réponse complète du menu public.
    
    Structure :
    - restaurant: infos du restaurant
    - menu: liste des catégories avec plats et accompagnements
    """
    restaurant: RestaurantMenuInfo
    menu: List[MenuCategoryPublic] = []

    class Config:
        json_schema_extra = {
            "example": {
                "restaurant": {
                    "name": "Le Petit Bistro",
                    "slug": "le-petit-bistro",
                    "logo_url": "https://example.com/logo.jpg",
                    "primary_color": "#FF5733",
                    "address": "123 Main Street",
                    "city": "Paris",
                    "country": "France",
                    "phone": "+33123456789",
                    "whatsapp": "+33123456789"
                },
                "menu": [
                    {
                        "category_id": "cat-uuid",
                        "name": "Plats",
                        "items": [
                            {
                                "id": "item-uuid",
                                "name": "Poulet braisé",
                                "description": "Poulet grillé aux épices",
                                "price": 3500,
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
