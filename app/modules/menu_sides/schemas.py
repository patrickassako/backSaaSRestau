from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class MenuSideCreate(BaseModel):
    """Schema for creating a menu item side/accompaniment."""
    menu_item_id: UUID
    name: str
    extra_price: float = 0
    is_required: bool = False
    position: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "menu_item_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Plantain frit",
                "extra_price": 500,
                "is_required": False,
                "position": 1
            }
        }


class MenuSideUpdate(BaseModel):
    """Schema for updating a menu item side."""
    name: Optional[str] = None
    extra_price: Optional[float] = None
    is_required: Optional[bool] = None
    position: Optional[int] = None


class MenuSideResponse(BaseModel):
    """Schema for menu side response."""
    id: UUID
    menu_item_id: UUID
    name: str
    extra_price: float
    is_required: bool
    position: int

    class Config:
        from_attributes = True
