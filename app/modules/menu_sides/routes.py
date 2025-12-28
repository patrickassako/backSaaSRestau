from uuid import UUID
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.modules.menu_sides import service
from app.modules.menu_sides.schemas import (
    MenuSideCreate,
    MenuSideUpdate,
    MenuSideResponse,
)

router = APIRouter(prefix="/menu", tags=["Menu Sides"])


@router.post("/items/{item_id}/sides", response_model=MenuSideResponse)
async def create_side(
    item_id: UUID,
    data: MenuSideCreate,
    user_id: UUID = Depends(get_current_user),
):
    """Create a new side/accompaniment for a menu item. Requires authentication."""
    # Override menu_item_id from path
    data.menu_item_id = item_id
    side = service.create_side(user_id, data)
    return side


@router.patch("/sides/{side_id}", response_model=MenuSideResponse)
async def update_side(
    side_id: UUID,
    data: MenuSideUpdate,
    user_id: UUID = Depends(get_current_user),
):
    """Update a menu side. Requires authentication."""
    side = service.update_side(user_id, side_id, data)
    return side


@router.delete("/sides/{side_id}", status_code=204)
async def delete_side(
    side_id: UUID,
    user_id: UUID = Depends(get_current_user),
):
    """Delete a menu side. Requires authentication."""
    service.delete_side(user_id, side_id)
    return None
