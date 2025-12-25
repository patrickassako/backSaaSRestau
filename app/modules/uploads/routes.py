from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from app.core.security import get_current_user
from app.modules.uploads import service
from app.modules.uploads.schemas import UploadResponse

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/avatar", response_model=UploadResponse)
async def upload_avatar(
    file: UploadFile = File(..., description="Avatar image file"),
    user_id: UUID = Depends(get_current_user),
):
    """
    Upload user avatar image.
    Requires authentication.
    Allowed file types: jpg, jpeg, png, gif, webp
    Maximum file size: 5MB
    """
    url = await service.upload_file_to_storage(
        file=file,
        folder="avatars",
        user_id=str(user_id),
    )

    return UploadResponse(url=url, message="Avatar uploaded successfully")


@router.post("/logo", response_model=UploadResponse)
async def upload_logo(
    file: UploadFile = File(..., description="Restaurant logo image file"),
    user_id: UUID = Depends(get_current_user),
):
    """
    Upload restaurant logo image.
    Requires authentication.
    Allowed file types: jpg, jpeg, png, gif, webp
    Maximum file size: 5MB
    """
    url = await service.upload_file_to_storage(
        file=file,
        folder="logos",
        user_id=str(user_id),
    )

    return UploadResponse(url=url, message="Logo uploaded successfully")
