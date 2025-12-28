"""
Service d'upload de fichiers vers Supabase Storage.
Gère les uploads d'avatars, logos et images de menu.
"""
import uuid
from fastapi import HTTPException, status, UploadFile
from app.core.supabase import get_supabase_client

# Extensions de fichiers autorisées pour les images
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}

# Taille maximale des fichiers : 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024


def validate_file(file: UploadFile) -> str:
    """
    Valide le fichier uploadé.
    Vérifie l'extension du fichier.
    
    Args:
        file: Fichier uploadé via FastAPI
        
    Returns:
        Extension du fichier en minuscules
        
    Raises:
        HTTPException: Si le type de fichier n'est pas autorisé
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nom du fichier est requis",
        )
    
    extension = file.filename.split(".")[-1].lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non autorisé. Types acceptés : {', '.join(ALLOWED_EXTENSIONS)}",
        )
    
    return extension


async def upload_file_to_storage(
    file: UploadFile,
    folder: str,
    user_id: str,
) -> str:
    """
    Upload un fichier vers Supabase Storage et retourne l'URL publique.
    
    Args:
        file: Fichier uploadé via FastAPI
        folder: Sous-dossier dans le bucket (ex: "avatars", "logos")
        user_id: ID de l'utilisateur pour organiser les fichiers
        
    Returns:
        URL publique du fichier uploadé
        
    Raises:
        HTTPException: En cas d'erreur de validation ou d'upload
    """
    supabase = get_supabase_client()

    # Valider le fichier et obtenir l'extension
    extension = validate_file(file)

    # Lire le contenu du fichier
    content = await file.read()

    # Vérifier la taille du fichier
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale : {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Générer un nom de fichier unique
    unique_filename = f"{folder}/{user_id}/{uuid.uuid4()}.{extension}"

    try:
        # Upload vers Supabase Storage
        supabase.storage.from_("restaurant-assets").upload(
            path=unique_filename,
            file=content,
            file_options={"content-type": file.content_type or "image/jpeg"},
        )

        # Obtenir l'URL publique
        public_url = supabase.storage.from_("restaurant-assets").get_public_url(
            unique_filename
        )

        return public_url

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload : {str(e)}",
        )


async def upload_menu_image_with_signed_url(
    file: UploadFile,
    user_id: str,
) -> str:
    """
    Upload une image de menu vers Supabase Storage et retourne une URL signée.
    
    Cette fonction est spécifiquement conçue pour les images de plats et 
    accompagnements du menu. Elle stocke les fichiers dans le sous-dossier 
    "menu-images" et génère une URL signée temporaire.
    
    Args:
        file: Fichier image uploadé (jpg, png, webp)
        user_id: ID de l'utilisateur propriétaire du restaurant
        
    Returns:
        URL signée valide pendant 1 heure (3600 secondes)
        
    Raises:
        HTTPException: 
            - 400 si le fichier est invalide ou trop volumineux
            - 500 si l'upload échoue
    """
    supabase = get_supabase_client()

    # Valider le fichier et obtenir l'extension
    extension = validate_file(file)

    # Lire le contenu du fichier
    content = await file.read()

    # Vérifier la taille du fichier (max 5MB)
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fichier trop volumineux. Taille maximale : {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    # Générer un nom de fichier unique dans le dossier menu-images
    unique_filename = f"menu-images/{user_id}/{uuid.uuid4()}.{extension}"

    try:
        # Upload vers Supabase Storage dans le bucket "restaurant-assets"
        supabase.storage.from_("restaurant-assets").upload(
            path=unique_filename,
            file=content,
            file_options={"content-type": file.content_type or "image/jpeg"},
        )

        # Générer une URL signée valide pendant 1 heure (3600 secondes)
        signed_url_response = supabase.storage.from_("restaurant-assets").create_signed_url(
            path=unique_filename,
            expires_in=3600  # 1 heure
        )

        # Extraire l'URL signée de la réponse
        if signed_url_response and "signedURL" in signed_url_response:
            return signed_url_response["signedURL"]
        elif signed_url_response and "signedUrl" in signed_url_response:
            return signed_url_response["signedUrl"]
        else:
            # Fallback vers l'URL publique si l'URL signée échoue
            public_url = supabase.storage.from_("restaurant-assets").get_public_url(
                unique_filename
            )
            return public_url

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'upload de l'image de menu : {str(e)}",
        )
