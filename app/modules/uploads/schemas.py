"""
Schémas Pydantic pour les réponses d'upload.
"""
from pydantic import BaseModel


class UploadResponse(BaseModel):
    """
    Schéma de réponse pour un upload réussi.
    
    Attributes:
        url: URL du fichier uploadé (publique ou signée selon l'endpoint)
        message: Message de confirmation
    """
    url: str
    message: str = "Fichier uploadé avec succès"

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://xxx.supabase.co/storage/v1/object/sign/restaurant-assets/menu-images/user123/abc123.jpg?token=xxx",
                "message": "Image de menu uploadée avec succès"
            }
        }
