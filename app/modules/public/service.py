"""
Service pour les endpoints publics.
Tous les endpoints de ce module sont accessibles sans authentification.
"""
from typing import Optional
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client


def get_public_restaurant_by_slug(slug: str) -> Optional[dict]:
    """
    Retourne les informations publiques d'un restaurant par son slug.
    
    Args:
        slug: Slug unique du restaurant
        
    Returns:
        Données publiques du restaurant
        
    Raises:
        HTTPException 404: Si le restaurant n'existe pas ou n'est pas actif
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("name, slug, description, logo_url, primary_color, address, city, country, phone, whatsapp")
            .eq("slug", slug)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        if "no rows" in str(e).lower() or "0 rows" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_public_menu_by_slug(slug: str) -> dict:
    """
    Retourne le menu complet public d'un restaurant.
    
    Accessible sans authentification (JWT non requis).
    Inclut les catégories, plats et accompagnements.
    
    Args:
        slug: Slug unique du restaurant
        
    Returns:
        Dictionnaire structuré avec :
        - restaurant: {name, slug, logo_url, primary_color, address, phone, whatsapp}
        - menu: liste des catégories avec leurs plats et accompagnements
        
    Raises:
        HTTPException 404: Si le restaurant n'existe pas ou n'est pas actif
        HTTPException 500: En cas d'erreur base de données
    """
    supabase = get_supabase_client()

    # ========================================
    # 1. Récupérer les infos du restaurant
    # ========================================
    try:
        restaurant = (
            supabase.table("restaurants")
            .select("id, name, slug, logo_url, primary_color, address, city, country, phone, whatsapp")
            .eq("slug", slug)
            .eq("is_active", True)
            .single()
            .execute()
        )

        if not restaurant.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant non trouvé",
            )

    except HTTPException:
        raise
    except Exception as e:
        if "no rows" in str(e).lower() or "0 rows" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant non trouvé",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )

    restaurant_id = restaurant.data["id"]

    # ========================================
    # 2. Récupérer les catégories actives
    # ========================================
    try:
        categories_response = (
            supabase.table("menu_categories")
            .select("id, name, position")
            .eq("restaurant_id", restaurant_id)
            .eq("is_active", True)
            .order("position")
            .execute()
        )

        categories = categories_response.data or []

    except Exception:
        categories = []

    # ========================================
    # 3. Récupérer les plats disponibles avec leurs accompagnements
    # ========================================
    try:
        items_response = (
            supabase.table("menu_items")
            .select("id, category_id, name, description, base_price, image_url, menu_item_sides(id, name, extra_price, is_required, position)")
            .eq("restaurant_id", restaurant_id)
            .eq("is_available", True)
            .order("position")
            .execute()
        )

        items = items_response.data or []

    except Exception:
        items = []

    # ========================================
    # 4. Construire la structure de réponse
    # ========================================
    menu_structure = []
    
    for category in categories:
        # Filtrer les plats de cette catégorie
        category_items = []
        
        for item in items:
            if item["category_id"] == category["id"]:
                # Trier les accompagnements par position
                sides = sorted(
                    item.get("menu_item_sides", []) or [],
                    key=lambda x: x.get("position", 0)
                )
                
                # Formater le plat
                category_items.append({
                    "id": item["id"],
                    "name": item["name"],
                    "description": item.get("description"),
                    "price": item["base_price"],  # Renommé de base_price à price
                    "image_url": item.get("image_url"),
                    "sides": [
                        {
                            "id": side["id"],
                            "name": side["name"],
                            "extra_price": side["extra_price"],
                        }
                        for side in sides
                    ]
                })

        # Ajouter la catégorie avec ses plats
        menu_structure.append({
            "category_id": category["id"],
            "name": category["name"],
            "items": category_items
        })

    # ========================================
    # 5. Retourner la réponse structurée
    # ========================================
    return {
        "restaurant": {
            "name": restaurant.data["name"],
            "slug": restaurant.data["slug"],
            "logo_url": restaurant.data.get("logo_url"),
            "primary_color": restaurant.data.get("primary_color"),
            "address": restaurant.data.get("address"),
            "city": restaurant.data.get("city"),
            "country": restaurant.data.get("country"),
            "phone": restaurant.data.get("phone"),
            "whatsapp": restaurant.data.get("whatsapp"),
        },
        "menu": menu_structure
    }
