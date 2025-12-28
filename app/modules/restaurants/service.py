"""
Service pour la gestion des restaurants.
Fournit les opérations CRUD et les fonctions publiques.
"""
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.restaurants.schemas import RestaurantCreate


def create_restaurant(user_id: UUID, data: RestaurantCreate) -> dict:
    """
    Crée un nouveau restaurant appartenant à l'utilisateur spécifié.
    Marque l'utilisateur comme "onboarded" après la création.
    
    Args:
        user_id: ID de l'utilisateur propriétaire
        data: Données du restaurant
        
    Returns:
        Restaurant créé
        
    Raises:
        HTTPException 400: Si la création échoue
        HTTPException 409: Si le slug existe déjà
        HTTPException 500: En cas d'erreur base de données
    """
    supabase = get_supabase_client()

    restaurant_data = {
        "name": data.name,
        "slug": data.slug,
        "owner_id": str(user_id),
        "description": data.description,
        "cuisine_type": data.cuisine_type,
        "phone": data.phone,
        "whatsapp": data.whatsapp,
        "email": data.email,
        "address": data.address,
        "city": data.city,
        "country": data.country,
        "logo_url": data.logo_url,
        "primary_color": data.primary_color,
        "is_active": True,
    }

    try:
        response = supabase.table("restaurants").insert(restaurant_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create restaurant",
            )

        # Mark user as onboarded after successful restaurant creation
        _mark_user_onboarded(user_id)

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        # Handle unique constraint violation for slug
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A restaurant with this slug already exists",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def _mark_user_onboarded(user_id: UUID) -> None:
    """
    Met à jour le profil utilisateur pour le marquer comme "onboarded".
    Appelé après la création réussie d'un restaurant.
    
    Args:
        user_id: ID de l'utilisateur
    """
    supabase = get_supabase_client()

    try:
        supabase.table("profiles").update({"is_onboarded": True}).eq(
            "id", str(user_id)
        ).execute()
    except Exception:
        # Log error but don't fail the restaurant creation
        # The onboarding status can be fixed later
        pass


def get_my_restaurants(user_id: UUID) -> List[dict]:
    """
    Retourne tous les restaurants appartenant à l'utilisateur.
    
    Args:
        user_id: ID de l'utilisateur propriétaire
        
    Returns:
        Liste des restaurants
        
    Raises:
        HTTPException 500: En cas d'erreur base de données
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("*")
            .eq("owner_id", str(user_id))
            .execute()
        )

        return response.data or []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}",
        )


def get_restaurant_by_slug(slug: str) -> Optional[dict]:
    """
    Retourne un restaurant par son slug (endpoint authentifié).
    Utilisé pour l'accès propriétaire - retourne toutes les données.
    
    Args:
        slug: Slug unique du restaurant
        
    Returns:
        Données complètes du restaurant
        
    Raises:
        HTTPException 404: Si le restaurant n'existe pas ou n'est pas actif
        HTTPException 500: En cas d'erreur base de données
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("*")
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


def get_public_restaurant_by_slug(slug: str) -> Optional[dict]:
    """
    Retourne un restaurant public par son slug.
    
    Accessible au rôle public (anon) via les policies RLS.
    Vérifie que le restaurant est actif ET onboarded.
    
    Args:
        slug: Slug unique du restaurant
        
    Returns:
        Données publiques du restaurant (sans owner_id ni données sensibles)
        Retourne None si aucun restaurant trouvé
        
    Raises:
        HTTPException 404: Si le restaurant n'existe pas, n'est pas actif,
                          ou n'est pas onboarded
        HTTPException 500: En cas d'erreur base de données
    """
    supabase = get_supabase_client()

    try:
        # Sélectionner uniquement les champs publics
        # Vérifier is_active=True ET is_onboarded=True
        response = (
            supabase.table("restaurants")
            .select(
                "id, name, slug, description, cuisine_type, logo_url, primary_color, "
                "address, city, country, phone, whatsapp, email"
            )
            .eq("slug", slug)
            .eq("is_active", True)
            .eq("is_onboarded", True)
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant non trouvé ou non disponible",
            )

        return response.data

    except HTTPException:
        raise
    except Exception as e:
        if "no rows" in str(e).lower() or "0 rows" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant non trouvé ou non disponible",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )


def user_has_restaurant(user_id: UUID) -> bool:
    """
    Vérifie si un utilisateur possède au moins un restaurant.
    Utilisé pour la vérification du flux d'onboarding.
    
    Args:
        user_id: ID de l'utilisateur
        
    Returns:
        True si l'utilisateur possède au moins un restaurant
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("restaurants")
            .select("id", count="exact")
            .eq("owner_id", str(user_id))
            .limit(1)
            .execute()
        )

        return response.count is not None and response.count > 0

    except Exception:
        # In case of error, return False to be safe
        return False
