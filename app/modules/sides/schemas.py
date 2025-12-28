"""
Schémas Pydantic pour les accompagnements (sides) de menu.
Utilisés pour la validation des entrées et les réponses API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class SideCreate(BaseModel):
    """
    Schéma pour créer un accompagnement.
    Le menu_item_id est renseigné via l'URL.
    """
    name: str = Field(..., min_length=1, description="Nom de l'accompagnement (obligatoire)")
    extra_price: float = Field(default=0, ge=0, description="Prix supplémentaire (≥ 0)")
    is_required: bool = Field(default=False, description="Accompagnement obligatoire ?")
    position: int = Field(default=0, description="Position d'affichage")
    image_url: Optional[str] = Field(default=None, description="URL de l'image (optionnel)")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Plantain frit",
                "extra_price": 500,
                "is_required": False,
                "position": 1,
                "image_url": "https://xxx.supabase.co/storage/v1/object/public/restaurant-assets/menu-images/side.jpg"
            }
        }


class SideUpdate(BaseModel):
    """
    Schéma pour modifier un accompagnement.
    Tous les champs sont optionnels.
    """
    name: Optional[str] = Field(default=None, min_length=1, description="Nom de l'accompagnement")
    extra_price: Optional[float] = Field(default=None, ge=0, description="Prix supplémentaire (≥ 0)")
    is_required: Optional[bool] = Field(default=None, description="Accompagnement obligatoire ?")
    position: Optional[int] = Field(default=None, description="Position d'affichage")
    image_url: Optional[str] = Field(default=None, description="URL de l'image")


class SideResponse(BaseModel):
    """
    Schéma de réponse pour un accompagnement.
    """
    id: UUID
    menu_item_id: UUID
    name: str
    extra_price: float
    is_required: bool
    position: int
    image_url: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "menu_item_id": "123e4567-e89b-12d3-a456-426614174001",
                "name": "Plantain frit",
                "extra_price": 500,
                "is_required": False,
                "position": 1,
                "image_url": None
            }
        }


class SidesListResponse(BaseModel):
    """
    Schéma de réponse pour la liste des accompagnements.
    """
    sides: List[SideResponse]


class SideDetailResponse(BaseModel):
    """
    Schéma de réponse pour un seul accompagnement.
    """
    side: SideResponse


class SideDeleteResponse(BaseModel):
    """
    Schéma de réponse pour la suppression.
    """
    message: str = "Side deleted"
