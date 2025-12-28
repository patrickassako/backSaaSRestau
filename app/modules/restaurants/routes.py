"""
Routes pour la gestion des restaurants.
Inclut les endpoints authentifiés et publics.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.restaurants import service
from app.modules.restaurants.schemas import (
    RestaurantCreate,
    RestaurantResponse,
    RestaurantPublicResponse,
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


# ============================================================
# ENDPOINTS AUTHENTIFIÉS (nécessitent JWT Bearer token)
# ============================================================

@router.post("", response_model=RestaurantResponse)
async def create_restaurant(
    data: RestaurantCreate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Crée un nouveau restaurant.
    
    - **Authentification requise** : Oui (JWT Bearer)
    - **Autorisation** : Le restaurant sera associé à l'utilisateur connecté
    
    Après création, l'utilisateur est automatiquement marqué comme "onboarded".
    """
    restaurant = service.create_restaurant(user_id=user_id, data=data)
    return restaurant


@router.get("/me", response_model=List[RestaurantResponse])
async def get_my_restaurants(
    user_id: UUID = Depends(get_current_user),
):
    """
    Récupère tous les restaurants de l'utilisateur connecté.
    
    - **Authentification requise** : Oui (JWT Bearer)
    """
    restaurants = service.get_my_restaurants(user_id=user_id)
    return restaurants


# ============================================================
# ENDPOINT PUBLIC (accessible sans authentification)
# ============================================================

@router.get("/{slug}", response_model=RestaurantPublicResponse)
async def get_public_restaurant(slug: str):
    """
    Récupère les informations publiques d'un restaurant par son slug.
    
    - **Authentification requise** : Non (accessible au rôle public/anon)
    - **Conditions** : Le restaurant doit être actif (is_active=True) 
                       ET onboarded (is_onboarded=True)
    - **Données retournées** : Uniquement les champs publics (pas de owner_id)
    
    **Exemple de réponse** :
    ```json
    {
        "id": "uuid",
        "name": "Le Petit Bistro",
        "slug": "le-petit-bistro",
        "description": "Restaurant français authentique",
        "cuisine_type": "French",
        "logo_url": "https://...",
        "primary_color": "#FF5733",
        "address": "123 Main Street",
        "city": "Paris",
        "country": "France",
        "phone": "+33123456789",
        "whatsapp": "+33123456789",
        "email": "contact@lepetitbistro.com"
    }
    ```
    
    **Codes d'erreur** :
    - 404 : Restaurant non trouvé ou non disponible (inactif/non onboarded)
    
    **Exemple curl** :
    ```bash
    curl -X GET "https://api.example.com/restaurants/le-petit-bistro"
    ```
    """
    restaurant = service.get_public_restaurant_by_slug(slug=slug)
    return restaurant
