from pydantic import BaseModel


class UploadResponse(BaseModel):
    """Schema for file upload response."""
    url: str
    message: str = "File uploaded successfully"

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.supabase.co/storage/v1/object/public/restaurant-assets/avatars/user123/image.jpg",
                "message": "File uploaded successfully"
            }
        }
