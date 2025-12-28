"""
Routes pour la gestion des accompagnements (sides) de menu.
Toutes les routes nécessitent une authentification JWT.
"""
from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.sides import service
from app.modules.sides.schemas import (
    SideCreate,
    SideUpdate,
    SideResponse,
    SidesListResponse,
    SideDetailResponse,
    SideDeleteResponse,
)

router = APIRouter(tags=["Sides (Accompagnements)"])


@router.get("/menu/items/{menu_item_id}/sides", response_model=SidesListResponse)
async def get_sides(
    menu_item_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """
    Liste tous les accompagnements d'un plat.
    
    - **Authentification requise** : Oui (JWT Bearer)
    - **Autorisation** : Propriétaire du restaurant uniquement
    
    **Exemple de réponse** :
    ```json
    {
        "sides": [
            {
                "id": "uuid",
                "menu_item_id": "uuid",
                "name": "Plantain frit",
                "extra_price": 500,
                "is_required": false,
                "position": 1,
                "image_url": null
            }
        ]
    }
    ```
    """
    sides = service.get_sides(menu_item_id=menu_item_id, user_id=user_id)
    return SidesListResponse(sides=sides)


@router.post("/menu/items/{menu_item_id}/sides", response_model=SideDetailResponse)
async def create_side(
    menu_item_id: UUID,
    data: SideCreate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Crée un nouvel accompagnement pour un plat.
    
    - **Authentification requise** : Oui (JWT Bearer)
    - **Autorisation** : Propriétaire du restaurant uniquement
    - **Validation** : nom obligatoire, extra_price ≥ 0
    
    **Exemple de requête** :
    ```json
    {
        "name": "Frites",
        "extra_price": 300,
        "is_required": false,
        "position": 2,
        "image_url": null
    }
    ```
    
    **Exemple de réponse** :
    ```json
    {
        "side": {
            "id": "uuid",
            "menu_item_id": "uuid",
            "name": "Frites",
            "extra_price": 300,
            "is_required": false,
            "position": 2,
            "image_url": null
        }
    }
    ```
    """
    side = service.create_side(menu_item_id=menu_item_id, user_id=user_id, data=data)
    return SideDetailResponse(side=side)


@router.patch("/menu/items/{menu_item_id}/sides/{side_id}", response_model=SideDetailResponse)
async def update_side(
    menu_item_id: UUID,
    side_id: UUID,
    data: SideUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """
    Met à jour un accompagnement existant.
    
    - **Authentification requise** : Oui (JWT Bearer)
    - **Autorisation** : Propriétaire du restaurant uniquement
    - **Validation** : extra_price ≥ 0 si fourni
    
    **Exemple de requête** :
    ```json
    {
        "name": "Frites maison",
        "extra_price": 400
    }
    ```
    
    **Exemple de réponse** :
    ```json
    {
        "side": {
            "id": "uuid",
            "menu_item_id": "uuid",
            "name": "Frites maison",
            "extra_price": 400,
            "is_required": false,
            "position": 2,
            "image_url": null
        }
    }
    ```
    """
    side = service.update_side(
        menu_item_id=menu_item_id,
        side_id=side_id,
        user_id=user_id,
        data=data,
    )
    return SideDetailResponse(side=side)


@router.delete("/menu/items/{menu_item_id}/sides/{side_id}", response_model=SideDeleteResponse)
async def delete_side(
    menu_item_id: UUID,
    side_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """
    Supprime un accompagnement.
    
    - **Authentification requise** : Oui (JWT Bearer)
    - **Autorisation** : Propriétaire du restaurant uniquement
    
    **Exemple de réponse** :
    ```json
    {
        "message": "Side deleted"
    }
    ```
    """
    service.delete_side(menu_item_id=menu_item_id, side_id=side_id, user_id=user_id)
    return SideDeleteResponse(message="Side deleted")
