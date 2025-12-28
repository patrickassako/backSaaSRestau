"""
Routes d'upload de fichiers.
Gère les uploads d'avatars, logos et images de menu vers Supabase Storage.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from app.core.security import get_current_user
from app.modules.uploads import service
from app.modules.uploads.schemas import UploadResponse

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/avatar", response_model=UploadResponse)
async def upload_avatar(
    file: UploadFile = File(..., description="Fichier image pour l'avatar"),
    user_id: UUID = Depends(get_current_user),
):
    """
    Upload d'un avatar utilisateur.
    
    - **Authentification requise** : Oui
    - **Types autorisés** : jpg, jpeg, png, gif, webp
    - **Taille max** : 5MB
    - **Stockage** : restaurant-assets/avatars/{user_id}/
    
    Retourne l'URL publique du fichier.
    """
    url = await service.upload_file_to_storage(
        file=file,
        folder="avatars",
        user_id=str(user_id),
    )

    return UploadResponse(url=url, message="Avatar uploadé avec succès")


@router.post("/logo", response_model=UploadResponse)
async def upload_logo(
    file: UploadFile = File(..., description="Fichier image pour le logo du restaurant"),
    user_id: UUID = Depends(get_current_user),
):
    """
    Upload d'un logo de restaurant.
    
    - **Authentification requise** : Oui
    - **Types autorisés** : jpg, jpeg, png, gif, webp
    - **Taille max** : 5MB
    - **Stockage** : restaurant-assets/logos/{user_id}/
    
    Retourne l'URL publique du fichier.
    """
    url = await service.upload_file_to_storage(
        file=file,
        folder="logos",
        user_id=str(user_id),
    )

    return UploadResponse(url=url, message="Logo uploadé avec succès")


@router.post("/menu_item_image", response_model=UploadResponse)
async def upload_menu_item_image(
    file: UploadFile = File(..., description="Image du plat ou accompagnement"),
    user_id: UUID = Depends(get_current_user),
):
    """
    Upload d'une image de plat ou accompagnement pour le menu.
    
    - **Authentification requise** : Oui (JWT Bearer token)
    - **Types autorisés** : jpg, jpeg, png, webp
    - **Taille max** : 5MB
    - **Stockage** : restaurant-assets/menu-images/{user_id}/
    
    **Réponse** :
    ```json
    {
        "url": "https://xxx.supabase.co/storage/v1/object/sign/restaurant-assets/menu-images/...",
        "message": "Image de menu uploadée avec succès"
    }
    ```
    
    L'URL retournée est une URL signée valide pendant 1 heure (3600 secondes).
    Pour un usage permanent, stockez le chemin et régénérez l'URL au besoin.
    
    **Codes d'erreur possibles** :
    - 400 : Fichier invalide (format non supporté ou taille > 5MB)
    - 401 : Non authentifié
    - 500 : Erreur serveur lors de l'upload
    """
    url = await service.upload_menu_image_with_signed_url(
        file=file,
        user_id=str(user_id),
    )

    return UploadResponse(url=url, message="Image de menu uploadée avec succès")
