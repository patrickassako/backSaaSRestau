"""
Service pour la gestion des accompagnements (sides) de menu.
Fournit les opérations CRUD avec vérification des droits d'accès.
"""
from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from app.core.supabase import get_supabase_client
from app.modules.sides.schemas import SideCreate, SideUpdate


def verify_menu_item_ownership(user_id: UUID, menu_item_id: UUID) -> bool:
    """
    Vérifie que l'utilisateur est propriétaire du restaurant 
    auquel appartient le plat.
    
    Args:
        user_id: ID de l'utilisateur authentifié
        menu_item_id: ID du plat à vérifier
        
    Returns:
        True si l'utilisateur est propriétaire, False sinon
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("menu_items")
            .select("*, restaurants!inner(owner_id)")
            .eq("id", str(menu_item_id))
            .single()
            .execute()
        )

        if not response.data:
            return False

        return response.data["restaurants"]["owner_id"] == str(user_id)

    except Exception:
        return False


def get_sides(menu_item_id: UUID, user_id: UUID) -> List[dict]:
    """
    Récupère tous les accompagnements d'un plat.
    
    Args:
        menu_item_id: ID du plat
        user_id: ID de l'utilisateur authentifié
        
    Returns:
        Liste des accompagnements triés par position
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas accès au plat
        HTTPException 500: En cas d'erreur base de données
    """
    # Vérifier les droits d'accès
    if not verify_menu_item_ownership(user_id, menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce plat",
        )

    supabase = get_supabase_client()

    try:
        response = (
            supabase.table("menu_item_sides")
            .select("*")
            .eq("menu_item_id", str(menu_item_id))
            .order("position")
            .execute()
        )

        return response.data or []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )


def create_side(menu_item_id: UUID, user_id: UUID, data: SideCreate) -> dict:
    """
    Crée un nouvel accompagnement pour un plat.
    
    Args:
        menu_item_id: ID du plat parent
        user_id: ID de l'utilisateur authentifié
        data: Données de l'accompagnement
        
    Returns:
        Accompagnement créé
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas accès au plat
        HTTPException 400: Si la création échoue
        HTTPException 500: En cas d'erreur base de données
    """
    # Vérifier les droits d'accès
    if not verify_menu_item_ownership(user_id, menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce plat",
        )

    supabase = get_supabase_client()

    # Préparer les données
    side_data = {
        "menu_item_id": str(menu_item_id),
        "name": data.name,
        "extra_price": data.extra_price,
        "is_required": data.is_required,
        "position": data.position,
        "image_url": data.image_url,
    }

    try:
        response = supabase.table("menu_item_sides").insert(side_data).execute()

        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Échec de la création de l'accompagnement",
            )

        return response.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )


def update_side(menu_item_id: UUID, side_id: UUID, user_id: UUID, data: SideUpdate) -> dict:
    """
    Met à jour un accompagnement existant.
    
    Args:
        menu_item_id: ID du plat parent (pour vérification)
        side_id: ID de l'accompagnement à modifier
        user_id: ID de l'utilisateur authentifié
        data: Nouvelles données
        
    Returns:
        Accompagnement mis à jour
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas accès
        HTTPException 404: Si l'accompagnement n'existe pas
        HTTPException 400: Si aucun champ à mettre à jour
        HTTPException 500: En cas d'erreur base de données
    """
    # Vérifier les droits d'accès via le plat
    if not verify_menu_item_ownership(user_id, menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce plat",
        )

    supabase = get_supabase_client()

    # Vérifier que le side appartient bien au menu_item
    try:
        existing = (
            supabase.table("menu_item_sides")
            .select("*")
            .eq("id", str(side_id))
            .eq("menu_item_id", str(menu_item_id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accompagnement non trouvé",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accompagnement non trouvé",
        )

    # Préparer les données de mise à jour (uniquement les champs fournis)
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun champ à mettre à jour",
        )

    try:
        response = (
            supabase.table("menu_item_sides")
            .update(update_data)
            .eq("id", str(side_id))
            .execute()
        )

        return response.data[0]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )


def delete_side(menu_item_id: UUID, side_id: UUID, user_id: UUID) -> None:
    """
    Supprime un accompagnement.
    
    Args:
        menu_item_id: ID du plat parent (pour vérification)
        side_id: ID de l'accompagnement à supprimer
        user_id: ID de l'utilisateur authentifié
        
    Raises:
        HTTPException 403: Si l'utilisateur n'a pas accès
        HTTPException 404: Si l'accompagnement n'existe pas
        HTTPException 500: En cas d'erreur base de données
    """
    # Vérifier les droits d'accès via le plat
    if not verify_menu_item_ownership(user_id, menu_item_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'avez pas accès à ce plat",
        )

    supabase = get_supabase_client()

    # Vérifier que le side appartient bien au menu_item
    try:
        existing = (
            supabase.table("menu_item_sides")
            .select("id")
            .eq("id", str(side_id))
            .eq("menu_item_id", str(menu_item_id))
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accompagnement non trouvé",
            )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Accompagnement non trouvé",
        )

    try:
        supabase.table("menu_item_sides").delete().eq("id", str(side_id)).execute()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur base de données : {str(e)}",
        )
