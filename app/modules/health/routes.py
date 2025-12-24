from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify backend status.
    """
    return {
        "status": "ok",
        "service": "restaurant-saas-backend"
    }
