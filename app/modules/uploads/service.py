import uuid
from fastapi import HTTPException, status, UploadFile
from app.core.supabase import get_supabase_client
from app.core.config import settings

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def validate_file(file: UploadFile) -> None:
    """
    Validates the uploaded file.
    Checks file extension and size.
    """
    # Check extension
    if file.filename:
        extension = file.filename.split(".")[-1].lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
            )


async def upload_file_to_storage(
    file: UploadFile,
    folder: str,
    user_id: str,
) -> str:
    """
    Uploads a file to Supabase storage.
    Returns the public URL of the uploaded file.
    """
    supabase = get_supabase_client()

    # Validate file
    validate_file(file)

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Generate unique filename
    extension = file.filename.split(".")[-1].lower() if file.filename else "jpg"
    unique_filename = f"{folder}/{user_id}/{uuid.uuid4()}.{extension}"

    try:
        # Upload to Supabase Storage
        response = supabase.storage.from_("restaurant-assets").upload(
            path=unique_filename,
            file=content,
            file_options={"content-type": file.content_type or "image/jpeg"},
        )

        # Get public URL
        public_url = supabase.storage.from_("restaurant-assets").get_public_url(
            unique_filename
        )

        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        )
