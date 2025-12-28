"""
Routes publiques accessibles sans authentification.
Utilisées par le site public Lovable pour afficher les restaurants et menus.
"""
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
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
    
    **Exemple curl** :
    ```bash
    curl -X GET "https://api.example.com/public/restaurants/le-petit-bistro/menu"
    ```
    """
    menu = service.get_public_menu_by_slug(slug)
    return menu


@router.get("/images/{image_path:path}")
async def get_public_image(image_path: str):
    """
    Sert les images publiques des restaurants (plats, logos, accompagnements).
    
    - **Authentification requise** : Non
    - **Comportement** : Redirige vers une signed URL Supabase (HTTP 302)
    - **Durée signed URL** : 1 heure (3600 secondes)
    
    **Chemins autorisés** :
    - menu-images/{user_id}/{filename}
    - logos/{user_id}/{filename}
    - avatars/{user_id}/{filename}
    
    **Exemple d'utilisation** :
    ```html
    <img src="https://api.example.com/public/images/menu-images/user123/image.jpg" />
    ```
    
    **Exemple curl** :
    ```bash
    curl -L "https://api.example.com/public/images/menu-images/user123/image.jpg"
    ```
    
    **Notes** :
    - Le navigateur suit automatiquement la redirection 302
    - Les images sont mises en cache par le navigateur
    - Pour Lovable, utilisez directement cette URL dans les balises img
    """
    signed_url = service.get_public_image_signed_url(image_path)
    return RedirectResponse(url=signed_url, status_code=302)
