"""
Routes publiques accessibles sans authentification.
Utilisées par le site public Lovable pour afficher les restaurants et menus.
"""
from fastapi import APIRouter
from app.modules.public import service
from app.modules.public.schemas import RestaurantPublicInfo, PublicMenuResponse

router = APIRouter(prefix="/public", tags=["Public"])


@router.get("/restaurants/{slug}", response_model=RestaurantPublicInfo)
async def get_public_restaurant(slug: str):
    """
    Récupère les informations publiques d'un restaurant.
    
    - **Authentification requise** : Non
    - **Condition** : Le restaurant doit être actif (is_active=True)
    
    **Exemple curl** :
    ```bash
    curl -X GET "https://api.example.com/public/restaurants/le-petit-bistro"
    ```
    """
    restaurant = service.get_public_restaurant_by_slug(slug)
    return restaurant


@router.get("/restaurants/{slug}/menu", response_model=PublicMenuResponse)
async def get_public_menu(slug: str):
    """
    Récupère le menu complet d'un restaurant.
    
    - **Authentification requise** : Non (accessible sans JWT)
    - **Condition** : Le restaurant doit être actif (is_active=True)
    
    Retourne les catégories, plats et accompagnements structurés.
    
    **Exemple de réponse** :
    ```json
    {
        "restaurant": {
            "name": "Le Petit Bistro",
            "slug": "le-petit-bistro",
            "logo_url": "https://...",
            "primary_color": "#FF5733",
            "address": "123 Main Street",
            "city": "Paris",
            "country": "France",
            "phone": "+33123456789",
            "whatsapp": "+33123456789"
        },
        "menu": [
            {
                "category_id": "uuid",
                "name": "Plats principaux",
                "items": [
                    {
                        "id": "uuid",
                        "name": "Poulet braisé",
                        "description": "Poulet aux épices africaines",
                        "price": 3500,
                        "image_url": "https://...",
                        "sides": [
                            {"id": "uuid", "name": "Plantain", "extra_price": 0},
                            {"id": "uuid", "name": "Frites", "extra_price": 500}
                        ]
                    }
                ]
            }
        ]
    }
    ```
    
    **Exemple curl** :
    ```bash
    curl -X GET "https://api.example.com/public/restaurants/le-petit-bistro/menu"
    ```
    
    **Codes d'erreur** :
    - 404 : Restaurant non trouvé ou inactif
    """
    menu = service.get_public_menu_by_slug(slug)
    return menu
